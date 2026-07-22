from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TERMINAL_STATES = {"PASS", "FAIL", "INTERRUPTED"}
ALLOWED_EXECUTABLES = {"python", "python.exe", "manim", "manim.exe", "ffmpeg", "ffmpeg.exe"}


def now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def process_is_alive(pid: Any) -> bool:
    if not isinstance(pid, int) or pid <= 0:
        return False
    if os.name == "nt":
        process_query_limited_information = 0x1000
        still_active = 259
        handle = ctypes.windll.kernel32.OpenProcess(process_query_limited_information, False, pid)
        if not handle:
            return False
        try:
            exit_code = ctypes.c_ulong()
            return bool(ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code))) and exit_code.value == still_active
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ValueError):
        return False


def reconcile_status(path: Path, status: dict[str, Any]) -> dict[str, Any]:
    if status.get("status") not in {"STARTING", "RUNNING"} or process_is_alive(status.get("pid")):
        return status
    status.update(
        status="INTERRUPTED",
        finished_at=now(),
        error="managed foreground render process is no longer alive",
    )
    atomic_json(path, status)
    return status


def inside(root: Path, raw: str, label: str) -> Path:
    path = Path(raw)
    resolved = (root / path).resolve() if not path.is_absolute() else path.resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"{label} must stay inside project_dir: {resolved}")
    return resolved


def extract_hash(path: Path, label: str) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"(?im)^\s*-?\s*{re.escape(label)}\s*:\s*`?([0-9a-f]{{64}})`?\s*$", text)
    if not match:
        raise ValueError(f"Missing {label} in {path.name}")
    return match.group(1).lower()


def require_pass(path: Path, kind: str) -> None:
    text = path.read_text(encoding="utf-8")
    patterns = {
        "review": r"(?im)^\s*(?:\*\*)?(?:Result\s*:\s*)?PASS(?:\*\*)?\s*$",
        "layout": r"(?im)^\s*Result\s*:\s*PASS\s*$",
    }
    if not re.search(patterns[kind], text):
        raise ValueError(f"{path.name} does not contain a formal PASS")


def expand_argv(argv: list[str]) -> list[str]:
    return [sys.executable if item == "{python}" else item for item in argv]


def resolve_executable(command: list[str]) -> str | None:
    executable = command[0]
    name = Path(executable).name.lower()
    if name not in ALLOWED_EXECUTABLES:
        return None
    return executable if Path(executable).is_file() else shutil.which(executable)


def windows_toast_app_id() -> str:
    powershell = shutil.which("powershell.exe")
    if not powershell:
        raise RuntimeError("Windows PowerShell 5.1 is unavailable")
    command = (
        "$ErrorActionPreference='Stop';"
        "[Console]::OutputEncoding=[System.Text.UTF8Encoding]::new();"
        "$apps=Get-StartApps;"
        "$names=@('PowerShell 7 (x64)','PowerShell 7','Windows PowerShell','Windows Terminal');"
        "foreach($name in $names){"
        "$match=$apps|Where-Object{$_.Name -eq $name}|Select-Object -First 1;"
        "if($match -and $match.AppID){[Console]::Write($match.AppID);exit 0}"
        "};"
        "throw 'No supported registered toast source was found'"
    )
    result = subprocess.run(
        [powershell, "-NoProfile", "-NonInteractive", "-Command", command],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=15,
    )
    app_id = result.stdout.strip()
    if result.returncode != 0 or not app_id:
        detail = result.stderr.strip() or "no registered App ID returned"
        raise RuntimeError(f"cannot resolve a registered Windows toast source: {detail}")
    return app_id


def windows_process_context(app_id: str) -> dict[str, Any]:
    session_id = ctypes.c_ulong()
    if not ctypes.windll.kernel32.ProcessIdToSessionId(os.getpid(), ctypes.byref(session_id)):
        raise RuntimeError("cannot resolve the current Windows Session ID")
    identity_result = subprocess.run(
        ["whoami.exe"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=10,
    )
    if identity_result.returncode != 0 or not identity_result.stdout.strip():
        raise RuntimeError("cannot resolve the current Windows identity")
    return {
        "mechanism": "Python PowerShell WinRT",
        "identity": identity_result.stdout.strip(),
        "session_id": session_id.value,
        "elevated": bool(ctypes.windll.shell32.IsUserAnAdmin()),
        "app_id": app_id,
    }


def notifier_fingerprint(context: Any) -> dict[str, Any]:
    if not isinstance(context, dict):
        return {}
    return {key: context.get(key) for key in ("mechanism", "identity", "session_id", "elevated", "app_id")}


def preflight(plan_path: Path, active_job_id: str | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    plan_path = plan_path.resolve()
    plan = load_json(plan_path)
    errors: list[str] = []
    checks: list[str] = []
    notification_context: dict[str, Any] | None = None

    if plan.get("version") != 1:
        errors.append("version must be 1")
    try:
        project = inside(plan_path.parent, str(plan["project_dir"]), "project_dir")
        if not project.is_dir():
            errors.append(f"project_dir does not exist: {project}")
    except (KeyError, ValueError) as exc:
        project = plan_path.parent
        errors.append(str(exc))

    paths: dict[str, Path] = {}
    for key in ("code_path", "handoff_path", "review_path", "layout_audit_path"):
        try:
            paths[key] = inside(project, str(plan[key]), key)
            if not paths[key].is_file():
                errors.append(f"missing required file: {paths[key]}")
        except (KeyError, ValueError) as exc:
            errors.append(str(exc))

    expected_hash = str(plan.get("expected_code_sha256", "")).lower()
    if not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
        errors.append("expected_code_sha256 must be 64 lowercase hex characters")
    elif "code_path" in paths and paths["code_path"].is_file():
        actual_hash = sha256(paths["code_path"])
        if actual_hash != expected_hash:
            errors.append(f"code hash mismatch: expected {expected_hash}, found {actual_hash}")
        else:
            checks.append("code hash matches plan")
        try:
            compile(paths["code_path"].read_text(encoding="utf-8"), str(paths["code_path"]), "exec")
            checks.append("scene source compiles")
        except (OSError, SyntaxError, UnicodeError) as exc:
            errors.append(f"scene source compile failed: {exc}")

    artifact_specs = (
        ("handoff_path", "Code SHA-256", None),
        ("review_path", "Reviewed Code SHA-256", "review"),
        ("layout_audit_path", "Audited Code SHA-256", "layout"),
    )
    for key, label, pass_kind in artifact_specs:
        path = paths.get(key)
        if not path or not path.is_file() or not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
            continue
        try:
            recorded = extract_hash(path, label)
            if recorded != expected_hash:
                errors.append(f"{path.name} hash does not match approved code")
            if pass_kind:
                require_pass(path, pass_kind)
            checks.append(f"{path.name} gate is valid")
        except (OSError, UnicodeError, ValueError) as exc:
            errors.append(str(exc))

    required_inputs = plan.get("required_inputs", [])
    if not isinstance(required_inputs, list):
        errors.append("required_inputs must be a list")
    else:
        for raw in required_inputs:
            try:
                path = inside(project, str(raw), "required input")
                if not path.is_file() or path.stat().st_size == 0:
                    errors.append(f"required input is missing or empty: {path}")
            except (OSError, ValueError) as exc:
                errors.append(str(exc))
        if required_inputs:
            checks.append(f"{len(required_inputs)} required inputs are present")

    scenes = plan.get("scene_outputs")
    if not isinstance(scenes, list) or len(scenes) != 6:
        errors.append("scene_outputs must contain exactly six entries")
        scenes = []
    output_paths: list[Path] = []
    for index, item in enumerate(scenes, 1):
        if not isinstance(item, dict) or not item.get("scene") or not item.get("path"):
            errors.append(f"scene_outputs[{index}] requires scene and path")
            continue
        try:
            output_paths.append(inside(project, str(item["path"]), f"scene output {index}"))
        except ValueError as exc:
            errors.append(str(exc))
    try:
        combined = inside(project, str(plan["combined_output"]), "combined_output")
        output_paths.append(combined)
    except (KeyError, ValueError) as exc:
        errors.append(str(exc))

    for key in ("manifest_path", "status_path", "log_path"):
        try:
            paths[key] = inside(project, str(plan[key]), key)
        except (KeyError, ValueError) as exc:
            errors.append(str(exc))

    for output in output_paths + [paths[key] for key in ("manifest_path", "status_path", "log_path") if key in paths]:
        output.parent.mkdir(parents=True, exist_ok=True)
        if not os.access(output.parent, os.W_OK):
            errors.append(f"output directory is not writable: {output.parent}")

    minimum_free = plan.get("minimum_free_bytes", 1_073_741_824)
    if not isinstance(minimum_free, int) or minimum_free < 0:
        errors.append("minimum_free_bytes must be a non-negative integer")
    else:
        free = shutil.disk_usage(project).free
        if free < minimum_free:
            errors.append(f"insufficient free disk space: {free} < {minimum_free}")
        else:
            checks.append(f"free disk space is {free} bytes")

    commands = plan.get("commands")
    if not isinstance(commands, list) or len(commands) < 7:
        errors.append("commands must contain at least six renders and one merge")
        commands = []
    covered_outputs: set[Path] = set()
    for index, item in enumerate(commands, 1):
        if not isinstance(item, dict) or not item.get("name") or not isinstance(item.get("argv"), list):
            errors.append(f"commands[{index}] requires name and argv list")
            continue
        argv = expand_argv([str(value) for value in item["argv"]])
        if not argv or resolve_executable(argv) is None:
            errors.append(f"commands[{index}] executable is missing or not allowed: {argv[:1]}")
        for raw in item.get("expected_outputs", []):
            try:
                covered_outputs.add(inside(project, str(raw), f"commands[{index}] expected output"))
            except ValueError as exc:
                errors.append(str(exc))
    for output in output_paths:
        if output not in covered_outputs:
            errors.append(f"no command claims the required output: {output}")

    allow_overwrite = plan.get("allow_overwrite", False)
    if not isinstance(allow_overwrite, bool):
        errors.append("allow_overwrite must be true or false")
    elif not allow_overwrite:
        for output in output_paths:
            if output.exists():
                errors.append(f"output already exists; set allow_overwrite only after confirming replacement: {output}")

    env = plan.get("env", {})
    if not isinstance(env, dict) or not all(isinstance(key, str) and isinstance(value, (str, int, float, bool)) for key, value in env.items()):
        errors.append("env must be an object with string keys and scalar values")

    notify_enabled = plan.get("notify", True)
    if not isinstance(notify_enabled, bool):
        errors.append("notify must be true or false")
    elif notify_enabled:
        system = platform.system()
        if system == "Windows":
            try:
                app_id = windows_toast_app_id()
                context = windows_process_context(app_id)
                if context.get("elevated"):
                    raise RuntimeError("desktop notification must run from the non-elevated desktop session")
                notification_context = notifier_fingerprint(context)
                checks.append(
                    "Python WinRT notifier preflight passed "
                    f"(identity={context.get('identity')}, session={context.get('session_id')}, app_id={app_id})"
                )
            except (OSError, RuntimeError) as exc:
                errors.append(str(exc))
        else:
            notifier = "osascript" if system == "Darwin" else "notify-send"
            if shutil.which(notifier) is None:
                errors.append(f"desktop notifier is unavailable: {notifier}")
            else:
                checks.append(f"desktop notifier is available: {notifier}")

    status = paths.get("status_path")
    if status and status.is_file():
        try:
            previous = reconcile_status(status, load_json(status))
            if previous.get("status") in {"STARTING", "RUNNING"} and previous.get("job_id") != active_job_id:
                errors.append(f"existing render job is still {previous['status']}: {previous.get('job_id')}")
        except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"cannot read existing status: {exc}")

    report = {
        "result": "PASS" if not errors else "FAIL",
        "checked_at": now(),
        "plan": str(plan_path),
        "project_dir": str(project),
        "checks": checks,
        "errors": errors,
    }
    if notification_context is not None:
        report["notification_context"] = notification_context
    return plan, report


def plan_paths(plan_path: Path, plan: dict[str, Any]) -> tuple[Path, Path, Path]:
    project = inside(plan_path.parent.resolve(), str(plan["project_dir"]), "project_dir")
    return (
        inside(project, str(plan["status_path"]), "status_path"),
        inside(project, str(plan["log_path"]), "log_path"),
        project,
    )


def notify(title: str, message: str, expected_context: dict[str, Any] | None = None) -> dict[str, Any]:
    system = platform.system()
    try:
        if system == "Windows":
            app_id = windows_toast_app_id()
            actual_context = notifier_fingerprint(windows_process_context(app_id))
            if expected_context is not None and actual_context != notifier_fingerprint(expected_context):
                raise RuntimeError(
                    f"notification environment changed: expected {notifier_fingerprint(expected_context)}, "
                    f"found {actual_context}"
                )
            env = os.environ.copy()
            env["RENDER_NOTIFY_TITLE"] = title
            env["RENDER_NOTIFY_MESSAGE"] = message
            env["RENDER_NOTIFY_APP_ID"] = app_id
            command = (
                "$ErrorActionPreference='Stop';"
                "[Windows.UI.Notifications.ToastNotificationManager,Windows.UI.Notifications,ContentType=WindowsRuntime]>$null;"
                "[Windows.Data.Xml.Dom.XmlDocument,Windows.Data.Xml.Dom.XmlDocument,ContentType=WindowsRuntime]>$null;"
                "$x=[Windows.Data.Xml.Dom.XmlDocument]::new();"
                "$x.LoadXml('<toast><visual><binding template=\"ToastGeneric\"><text></text><text></text></binding></visual></toast>');"
                "$n=$x.GetElementsByTagName('text');$n.Item(0).AppendChild($x.CreateTextNode($env:RENDER_NOTIFY_TITLE))>$null;"
                "$n.Item(1).AppendChild($x.CreateTextNode($env:RENDER_NOTIFY_MESSAGE))>$null;"
                "$t=[Windows.UI.Notifications.ToastNotification]::new($x);"
                "[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($env:RENDER_NOTIFY_APP_ID).Show($t)"
            )
            subprocess.run(
                ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
                env=env,
                check=True,
                timeout=15,
            )
            return {
                "submitted": True,
                "attempted_at": now(),
                "channel": "Python PowerShell WinRT desktop",
                "context": actual_context,
            }
        if system == "Darwin":
            script = 'display notification (system attribute "RENDER_NOTIFY_MESSAGE") with title (system attribute "RENDER_NOTIFY_TITLE")'
            env = os.environ.copy()
            env.update(RENDER_NOTIFY_TITLE=title, RENDER_NOTIFY_MESSAGE=message)
            subprocess.run(["osascript", "-e", script], env=env, check=True, timeout=15)
        else:
            subprocess.run(["notify-send", title, message], check=True, timeout=15)
        return {"submitted": True, "attempted_at": now(), "channel": f"{system} desktop"}
    except Exception as exc:
        return {"submitted": False, "attempted_at": now(), "channel": f"{system} desktop", "error": str(exc)}


def write_manifest(plan_path: Path, plan: dict[str, Any], project: Path) -> Path:
    manifest = inside(project, str(plan["manifest_path"]), "manifest_path")
    code = inside(project, str(plan["code_path"]), "code_path")
    lines = [
        "# Render Manifest", "", "## Approved Source", "",
        f"- Code path: `{code}`", f"- Code SHA-256: `{sha256(code)}`",
        f"- Review result: `{plan['review_path']}`", "- Review status: `PASS`",
        f"- Layout audit result: `{plan['layout_audit_path']}`", "- Layout audit status: `PASS`",
        f"- Render job plan: `{plan_path}`", "", "## Render Outputs", "",
        "| 順序 | Scene | MP4 路徑 | 最後修改時間 | 檔案大小 |",
        "| --- | --- | --- | --- | ---: |",
    ]
    for index, item in enumerate(plan["scene_outputs"], 1):
        output = inside(project, str(item["path"]), "scene output")
        stat = output.stat()
        lines.append(f"| {index} | `{item['scene']}` | `{output}` | `{datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(timespec='seconds')}` | `{stat.st_size}` |")
    combined = inside(project, str(plan["combined_output"]), "combined_output")
    stat = combined.stat()
    lines += ["", "## Combined Output", "", f"- Combined MP4: `{combined}`", f"- MP4 last-write time: `{datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(timespec='seconds')}`", f"- MP4 size: `{stat.st_size}`", f"- MP4 SHA-256: `{sha256(combined)}`", ""]
    manifest.write_text("\n".join(lines), encoding="utf-8")
    return manifest


def worker(plan_path: Path, job_id: str) -> int:
    plan = load_json(plan_path)
    status_path, log_path, project = plan_paths(plan_path, plan)
    started = now()
    state: dict[str, Any] = {
        "job_id": job_id,
        "status": "RUNNING",
        "backend": "managed_foreground",
        "pid": os.getpid(),
        "started_at": started,
        "heartbeat_at": started,
        "current_command": None,
        "command_pid": None,
        "plan": str(plan_path),
        "log": str(log_path),
        "acknowledged_at": None,
    }
    try:
        launch_state = load_json(status_path)
        if launch_state.get("job_id") != job_id or launch_state.get("status") != "STARTING":
            raise RuntimeError("worker requires the matching STARTING status created by the launcher")
        _, worker_report = preflight(plan_path, active_job_id=job_id)
        if worker_report["result"] != "PASS":
            raise RuntimeError("worker preflight failed: " + "; ".join(worker_report["errors"]))
        if platform.system() == "Windows" and plan.get("notify", True):
            launch_context = notifier_fingerprint(launch_state.get("notification_context"))
            worker_context = notifier_fingerprint(worker_report.get("notification_context"))
            if launch_context != worker_context:
                raise RuntimeError(f"notification environment changed before render: {launch_context} != {worker_context}")
            state["notification_context"] = worker_context
        atomic_json(status_path, state)
        print(json.dumps(state, ensure_ascii=False, indent=2), flush=True)
        with log_path.open("a", encoding="utf-8") as log:
            log.write(f"[{started}] job {job_id} started\n")
            for index, item in enumerate(plan["commands"], 1):
                code = inside(project, str(plan["code_path"]), "code_path")
                if sha256(code) != str(plan["expected_code_sha256"]).lower():
                    raise RuntimeError("approved scene code changed while render job was running")
                argv = expand_argv([str(value) for value in item["argv"]])
                log.write(f"[{now()}] command {index}: {item['name']}\nargv={json.dumps(argv, ensure_ascii=False)}\n")
                log.flush()
                command_process = subprocess.Popen(
                    argv,
                    cwd=project,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    text=True,
                    env={**os.environ, **{str(k): str(v) for k, v in plan.get("env", {}).items()}},
                )
                state.update(current_command=item["name"], command_pid=command_process.pid, heartbeat_at=now())
                atomic_json(status_path, state)
                while True:
                    try:
                        return_code = command_process.wait(timeout=5)
                        break
                    except subprocess.TimeoutExpired:
                        state["heartbeat_at"] = now()
                        atomic_json(status_path, state)
                state.update(current_command=None, command_pid=None, heartbeat_at=now())
                atomic_json(status_path, state)
                if return_code != 0:
                    raise RuntimeError(f"command failed ({return_code}): {item['name']}")
                for raw in item.get("expected_outputs", []):
                    output = inside(project, str(raw), "expected output")
                    if not output.is_file() or output.stat().st_size == 0:
                        raise RuntimeError(f"command did not create a non-empty output: {output}")
            for item in plan["scene_outputs"]:
                output = inside(project, str(item["path"]), "scene output")
                if not output.is_file() or output.stat().st_size == 0:
                    raise RuntimeError(f"missing or empty Scene MP4: {output}")
            combined = inside(project, str(plan["combined_output"]), "combined_output")
            if not combined.is_file() or combined.stat().st_size == 0:
                raise RuntimeError(f"missing or empty combined MP4: {combined}")
            manifest = write_manifest(plan_path, plan, project)
            state.update(status="PASS", finished_at=now(), heartbeat_at=now(), current_command=None, command_pid=None, manifest=str(manifest), combined_mp4=str(combined))
            atomic_json(status_path, state)
            state["notification"] = notify(
                "Manim render completed",
                f"PASS: {combined}",
                state.get("notification_context"),
            ) if plan.get("notify", True) else {"submitted": False, "channel": "disabled"}
            atomic_json(status_path, state)
            return 0
    except Exception as exc:
        state.update(status="FAIL", finished_at=now(), heartbeat_at=now(), current_command=None, command_pid=None, error=str(exc), traceback=traceback.format_exc())
        atomic_json(status_path, state)
        state["notification"] = notify(
            "Manim render failed",
            f"FAIL: {exc}. See {log_path}",
            state.get("notification_context"),
        ) if plan.get("notify", True) else {"submitted": False, "channel": "disabled"}
        atomic_json(status_path, state)
        return 1


def start(plan_path: Path) -> int:
    plan, report = preflight(plan_path)
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
    if report["result"] != "PASS":
        return 1
    status_path, _, _ = plan_paths(plan_path.resolve(), plan)
    job_id = f"render-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
    starting = {
        "job_id": job_id,
        "status": "STARTING",
        "backend": "managed_foreground",
        "pid": os.getpid(),
        "started_at": now(),
        "plan": str(plan_path.resolve()),
        "status_path": str(status_path),
        "notification_context": report.get("notification_context"),
        "acknowledged_at": None,
    }
    atomic_json(status_path, starting)
    print(json.dumps(starting, ensure_ascii=False, indent=2), flush=True)
    return worker(plan_path.resolve(), job_id)


def main() -> int:
    parser = argparse.ArgumentParser(description="Preflight, run, and inspect a managed foreground Manim render job.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("preflight", "start", "status", "ack"):
        subparsers.add_parser(name).add_argument("path", type=Path)
    args = parser.parse_args()
    if args.command == "preflight":
        _, report = preflight(args.path)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["result"] == "PASS" else 1
    if args.command == "start":
        return start(args.path)
    status_path = args.path.resolve()
    status = reconcile_status(status_path, load_json(status_path))
    if args.command == "ack":
        if status.get("status") not in TERMINAL_STATES:
            print(json.dumps(status, ensure_ascii=False, indent=2))
            return 1
        status["acknowledged_at"] = now()
        atomic_json(status_path, status)
    print(json.dumps(status, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

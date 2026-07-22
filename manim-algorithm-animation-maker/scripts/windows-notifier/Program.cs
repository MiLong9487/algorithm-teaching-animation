using System.Diagnostics;
using System.Security.Principal;
using System.Text.Json;
using Microsoft.Windows.AppNotifications;
using Microsoft.Windows.AppNotifications.Builder;

static string ToJson(object value) => JsonSerializer.Serialize(value);

var mode = args.Length > 0 ? args[0].ToLowerInvariant() : "";
if (mode != "probe" && (mode != "notify" || args.Length != 3))
{
    Console.Error.WriteLine(ToJson(new
    {
        submitted = false,
        error = "usage: ManimRenderNotifier.exe probe | notify <title> <message>"
    }));
    return 2;
}

var manager = AppNotificationManager.Default;
var registered = false;
try
{
    manager.NotificationInvoked += (_, _) => { };
    manager.Register();
    registered = true;

    var context = new
    {
        mechanism = "Windows App SDK",
        process = Environment.ProcessPath,
        identity = WindowsIdentity.GetCurrent().Name,
        session_id = Process.GetCurrentProcess().SessionId,
        elevated = new WindowsPrincipal(WindowsIdentity.GetCurrent()).IsInRole(WindowsBuiltInRole.Administrator)
    };

    if (mode == "probe")
    {
        Console.WriteLine(ToJson(new { result = "PASS", context }));
        return 0;
    }

    var notification = new AppNotificationBuilder()
        .AddText(args[1])
        .AddText(args[2])
        .BuildNotification();
    manager.Show(notification);
    Console.WriteLine(ToJson(new { submitted = true, context }));
    return 0;
}
catch (Exception exception)
{
    Console.Error.WriteLine(ToJson(new
    {
        submitted = false,
        exception = exception.GetType().FullName,
        hresult = $"0x{exception.HResult:X8}",
        error = exception.Message,
        identity = WindowsIdentity.GetCurrent().Name,
        session_id = Process.GetCurrentProcess().SessionId
    }));
    return 1;
}
finally
{
    if (registered)
    {
        manager.Unregister();
    }
}

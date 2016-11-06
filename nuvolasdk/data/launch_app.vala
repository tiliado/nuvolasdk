/*
 * Copyright 2016 Jiří Janoušek <janousek.jiri@gmail.com>
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met: 
 * 
 * 1. Redistributions of source code must retain the above copyright notice, this
 *    list of conditions and the following disclaimer. 
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution. 
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
 * ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

namespace Nuvolasdk
{

extern const string APP_ID;

MainLoop loop = null;
int retcode = 0;
CommandLine cmd_line = null;

[DBus (name="org.gtk.private.CommandLine")]
public class CommandLine : GLib.Object
{
	public CommandLine()
	{
	}
	
	public void print(string text)
	{
		stdout.puts(text);
	}
	
	public void print_error(string text)
	{
		stderr.puts(text);
	}
}

private async void launch(Variant args) throws GLib.Error
{
	var conn = yield Bus.@get(BusType.SESSION, null);
	cmd_line = new CommandLine();
	var cmd_line_path = "/eu/tiliado/NuvolaSdk/CommandLine";
	conn.register_object<CommandLine>(cmd_line_path, cmd_line);
	var app_proxy = yield DBusProxy.@new(
		conn, DBusProxyFlags.DO_NOT_LOAD_PROPERTIES|DBusProxyFlags.DO_NOT_CONNECT_SIGNALS, null,
		"eu.tiliado.Nuvola", "/eu/tiliado/Nuvola", "org.gtk.Application", null);
	var platform = new VariantBuilder(new VariantType("a{sv}"));
	platform.add("{sv}", "cwd", new Variant.bytestring(Environment.get_current_dir()));
	platform.add("{sv}", "desktop-startup-id", new Variant.string("0"));
	var params = new Variant("(o@aaya{sv})", cmd_line_path, args, platform);
	var result = yield app_proxy.call("CommandLine", params, 0, -1, null);
	result.get("(i)", out retcode);
}

int main(string[] argv)
{
	var builder = new VariantBuilder(new VariantType("aay"));
	builder.add_value(new Variant.bytestring(argv[0]));
	builder.add_value(new Variant.bytestring("-a"));
	builder.add_value(new Variant.bytestring(APP_ID));
	for (var i = 1; i < argv.length; i++)
		builder.add_value(new Variant.bytestring(argv[i]));
	var args = builder.end();
	loop = new MainLoop();
	launch.begin(args, on_launch_done);
	loop.run();
	return retcode;
}

private void on_launch_done(GLib.Object? o, AsyncResult res)
{
	try
	{
		launch.end(res);
	}
	catch (GLib.Error e)
	{
		stderr.printf("Failed to launch the application. %s\n", e.message);
	}
	Idle.add(() => {loop.quit(); return false;});
}

}

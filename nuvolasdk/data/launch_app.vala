/*
 * Copyright 2016-2017 Jiří Janoušek <janousek.jiri@gmail.com>
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
extern const string UNIQUE_ID;
extern const string APP_DATA_DIR;
extern const bool FLATPAK_BUILD;


struct Args
{
	static bool debug;
	static bool verbose;
	static bool version;
	
	public const OptionEntry[] options =
	{
		{ "verbose", 'v', 0, OptionArg.NONE, ref Args.verbose, "Print informational messages", null },
		{ "debug", 'D', 0, OptionArg.NONE, ref Args.debug, "Print debugging messages", null },
		{ "version", 'V', 0, OptionArg.NONE, ref Args.version, "Print version and exit", null },
		{ null }
	};
}


StringBuilder stdout_buf = null;
StringBuilder stderr_buf = null;

int main(string[] argv)
{	
	try
	{
		var opt_context = new OptionContext("- %s".printf(Nuvola.get_app_name()));
		opt_context.set_help_enabled(true);
		opt_context.add_main_entries(Args.options, null);
		opt_context.set_ignore_unknown_options(true);  // e.g. --gapplication-service
		opt_context.parse(ref argv);
	}
	catch (OptionError e)
	{
		stderr.printf("option parsing failed: %s\n", e.message);
		return 1;
	}
	
	Diorite.Logger.init(stderr, Args.debug ? GLib.LogLevelFlags.LEVEL_DEBUG
	  : (Args.verbose ? GLib.LogLevelFlags.LEVEL_INFO: GLib.LogLevelFlags.LEVEL_WARNING),
	  true, "Runner");
	
	var app_dir = File.new_for_path(Environment.get_variable("NUVOLASDK_APP_DATA_DIR") ?? APP_DATA_DIR);
	debug("App data dir: %s", app_dir.get_path());
	if (Args.version)
		return Nuvola.Startup.print_web_app_version(stdout, app_dir);
	
	try
	{
		return Nuvola.Startup.run_web_app_with_dbus_handshake(app_dir, argv);
	}
	catch (Nuvola.WebAppError e)
	{
		show_error("Failed to load web app '%s'.\n%s".printf(APP_ID, e.message));
		return 2;
	}
}

private void show_error(string error)
{
	stderr.printf("%s\n", error);
	string[] _args = {};
	unowned string[] args = _args;
	Gtk.init(ref args);
	var window = new Gtk.Window();
	window.set_default_size(250, -1);
	var grid = new Gtk.Grid();
	grid.margin = 15;
	grid.row_spacing = 15;
	window.add(grid);
	var text = "Failed to launch the application.";
	#if FLATPAK
		text +="\n\nIs the eu.tiliado.Nuvola flatpak installed?";
	#endif
	var label = new Gtk.Label(text);
	label.set_line_wrap(true);
	label.selectable = true;
	grid.add(label);
	grid.orientation = Gtk.Orientation.VERTICAL;
	var text_view = new Gtk.TextView();
	grid.add(text_view);
	text_view.editable = false;
	text_view.hexpand = true;
	text_view.wrap_mode = Gtk.WrapMode.WORD_CHAR;
	var buffer = text_view.buffer;
	buffer.insert_at_cursor(error, -1);
	buffer.insert_at_cursor("\n", -1);
	if (stdout_buf != null && stdout_buf.len > 0)
	{
		buffer.insert_at_cursor(stdout_buf.str, (int) stdout_buf.len);
		buffer.insert_at_cursor("\n", -1);
	}
	if (stderr_buf != null && stderr_buf.len > 0)
	{
		buffer.insert_at_cursor(stderr_buf.str, (int) stderr_buf.len);
		buffer.insert_at_cursor("\n", -1);
	}
	window.delete_event.connect((e) => {Gtk.main_quit(); return false;});
	window.show_all();
	label.select_region(0, 0);
	Gtk.main();
}

}

"""
Example of using CEF browser in off-screen rendering mode
(windowless) to create a screenshot of a web page. This
example doesn't depend on any third party GUI framework.
This example is discussed in Tutorial in the Off-screen
rendering section.

Usage:
    python screenshot.py
Tested configurations:
- CEF Python v57.0+
"""

from cefpython3 import cefpython as cef
import os
import platform
import subprocess
import sys

# Config
#URL = "https://github.com/cztomczak/cefpython"
URL = 'http://www.dmm.co.jp/en/search/=/searchstr=CEMN00004'

def main():
    check_versions()
    sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
    # Off-screen-rendering requires setting "windowless_rendering_enabled"
    # option, so that RenderHandler callbacks are called.
    cef.Initialize(settings={"windowless_rendering_enabled": True})
    create_browser()
    cef.MessageLoop()
    cef.Shutdown()

def check_versions():
    ver = cef.GetVersion()
    print("[screenshot.py] CEF Python {ver}".format(ver=ver["version"]))
    print("[screenshot.py] Chromium {ver}".format(ver=ver["chrome_version"]))
    print("[screenshot.py] CEF {ver}".format(ver=ver["cef_version"]))
    print("[screenshot.py] Python {ver} {arch}".format(
           ver=platform.python_version(),
           arch=platform.architecture()[0]))
    assert cef.__version__ >= "57.0", "CEF Python v57.0+ required to run this"


def create_browser():
    # Create browser in off-screen-rendering mode (windowless mode)
    # by calling SetAsOffscreen method. In such mode parent window
    # handle can be NULL (0).
    parent_window_handle = 0
    window_info = cef.WindowInfo()
    window_info.SetAsOffscreen(parent_window_handle)
    print("[screenshot.py] Loading url: {url}"
          .format(url=URL))

    browser = cef.CreateBrowserSync(window_info=window_info,
                                    url=URL)
    browser.SetClientHandler(LoadHandler())
    browser.SetClientHandler(RequestHandler())
    browser.SendFocusEvent(True)
    # You must call WasResized at least once to let know CEF that
    # viewport size is available and that OnPaint may be called.
    browser.WasResized()


def exit_app(browser):
    # Important note:
    #   Do not close browser nor exit app from OnLoadingStateChange
    #   OnLoadError or OnPaint events. Closing browser during these
    #   events may result in unexpected behavior. Use cef.PostTask
    #   function to call exit_app from these events.
    print("[screenshot.py] Close browser and exit app")
    browser.CloseBrowser()
    cef.QuitMessageLoop()

class Visitor(object):
    def Visit(self, value):
        print("[screenshot.py] get html source")
        fname = 'dmm_result.html'
        with open(fname, 'wb') as f:
            f.write(value.encode())
        print('save %s' % fname)

class RequestHandler(object):
    def OnResourceRedirect(self, browser, frame, old_url, new_url_out, **_):
        print('{} redirected from {}'.format(new_url_out, old_url))

#    def OnBeforeResourceLoad(self, browser, frame, request):
#        print('header: {}'.format(request.GetHeader()))

    def OnBeforeBrowse(self, browser, frame, request, is_redirect):
        print('redirected:{}'.format(is_redirect))
        print('header: {}'.format(request.GetHeaderMap()))

        return False

class LoadHandler(object):
    _visitor = Visitor()
    def OnLoadingStateChange(self, browser, is_loading, **_):
        """Called when the loading state has changed."""
        if not is_loading:
            # Loading is complete
            sys.stdout.write(os.linesep)
            print("[screenshot.py] Web page loading is complete")
            # See comments in exit_app() why PostTask must be used
            browser.GetMainFrame().GetSource(self._visitor)

            cef.PostTask(cef.TID_UI, exit_app, browser)

    def OnLoadError(self, browser, frame, error_code, failed_url, **_):
        """Called when the resource load for a navigation fails
        or is canceled."""
        if not frame.IsMain():
            # We are interested only in loading main url.
            # Ignore any errors during loading of other frames.
            return
        print("[screenshot.py] ERROR: Failed to load url: {url}"
              .format(url=failed_url))
        print("[screenshot.py] Error code: {code}"
              .format(code=error_code))
        # See comments in exit_app() why PostTask must be used
        cef.PostTask(cef.TID_UI, exit_app, browser)

if __name__ == '__main__':
    main()

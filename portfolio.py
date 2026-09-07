import pathlib
import streamlit as st

st.set_page_config(
    page_title="Atlas Terminal · Portfolio Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

html_path = pathlib.Path(__file__).parent / "portfolio-manager" / "project" / "Portfolio Manager.html"
html_content = html_path.read_text(encoding="utf-8")

# Inject JS into the offline HTML that reaches up to the parent Streamlit page,
# hides all Streamlit chrome, and pins this iframe to fill the full viewport.
inject = """<script>
(function() {
    try {
        var p = window.parent;
        var s = p.document.createElement('style');
        s.textContent =
            '#MainMenu,header,footer,' +
            '[data-testid="stToolbar"],[data-testid="stDecoration"],' +
            '[data-testid="stStatusWidget"],[data-testid="stSidebarCollapsedControl"],' +
            'section[data-testid="stSidebar"],.stDeployButton{display:none!important}' +
            '.main .block-container{padding:0!important;max-width:100vw!important;margin:0!important}' +
            'body,.stApp{overflow:hidden!important;background:#050816!important}';
        p.document.head.appendChild(s);

        function pin() {
            p.document.querySelectorAll('iframe').forEach(function(f) {
                f.style.cssText =
                    'position:fixed;top:0;left:0;' +
                    'width:100vw;height:100vh;' +
                    'border:none;z-index:9999;';
            });
        }
        [0, 150, 400, 900, 2000].forEach(function(t) { setTimeout(pin, t); });
        p.addEventListener('resize', pin);
    } catch(e) {}
})();
</script>"""

html_with_inject = html_content.replace('</head>', inject + '\n</head>', 1)
st.iframe(html_with_inject, width="stretch", height="stretch")

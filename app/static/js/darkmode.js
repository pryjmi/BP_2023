document.addEventListener("DOMContentLoaded", toggle);
function toggle() {

    const auto_dm = document.getElementById('auto-dark-mode-switch');
    const toggle_dm = document.getElementById('toggle-dark-mode-switch');

    auto_dm.addEventListener("change", cb_switch)
    auto_dm.addEventListener("change", cb_switch3)
    toggle_dm.addEventListener("change", cb_switch2)

    /*
    if (window.matchMedia('(prefers-color-scheme: dark)')) {
        auto_darkmode();
    } else {
        auto_nodark();
    }
    */

    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
        if (event.matches) {
            auto_darkmode();
        } else {
            auto_nodark();
        }
    })

    function cb_switch() {
        if (auto_dm.checked) {
            localStorage.setItem("auto_dm_checked", auto_dm.checked = true)
            localStorage.setItem("toggle_dm_checked", toggle_dm.checked = false)
            localStorage.setItem("toggle_dm_disabled", toggle_dm.disabled = true)
        } else {
            localStorage.setItem("auto_dm_checked", auto_dm.checked = false)
            localStorage.setItem("toggle_dm_disabled", toggle_dm.disabled = false)
        }
        cb_switch2();
    }

    function cb_switch3() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            auto_darkmode();
        } else {
            auto_nodark();
        }
    }

    function cb_switch2() {
        if (toggle_dm.checked) {
            localStorage.setItem("auto_dm_checked", auto_dm.checked = false)
            localStorage.setItem("toggle_dm_checked", toggle_dm.checked = true)
            darkmode()
        } else {
            localStorage.setItem("toggle_dm_checked", toggle_dm.checked = false)
            nodark()
        }
    }

    auto_dm.checked = JSON.parse(localStorage.getItem("auto_dm_checked"));
    toggle_dm.checked = JSON.parse(localStorage.getItem("toggle_dm_checked"));
    toggle_dm.disabled = JSON.parse(localStorage.getItem("toggle_dm_disabled"));

    function auto_darkmode() {
        if (auto_dm.checked) {
            document.body.classList.toggle("dark-mode");
            toggle_dm.checked = true;
            localStorage.setItem("mode", "dark");
        } else {
            document.body.classList.remove("dark-mode");
            toggle_dm.checked = false;
            localStorage.setItem("mode", "light");
        }
    }

    function auto_nodark() {
        toggle_dm.checked = false;
        if (!toggle_dm.checked) {
            document.body.classList.remove("dark-mode");
            localStorage.setItem("mode", "light");
        }
    }

    function darkmode() {
        document.body.classList.toggle("dark-mode");
        toggle_dm.checked = true;
        localStorage.setItem("mode", "dark");
    }

    function nodark() {
        document.body.classList.remove("dark-mode");
        toggle_dm.checked = false;
        localStorage.setItem("mode", "light");
    }

    if (localStorage.getItem("mode") == "dark") {
        darkmode();
    } else {
        nodark();
    }
}
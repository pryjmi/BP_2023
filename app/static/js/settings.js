document.addEventListener("DOMContentLoaded", toggle);

function toggle() {
    settings = document.getElementById("settings_div")
    button = document.getElementById("settings_btn")

    button.addEventListener("click", settings_func)
    body = document.getElementsByTagName("body")[0];

    function settings_func() {
        if (settings.style.display === "block") {
            settings.style.display = "none";
        } else {
            settings.style.display = "block"
        }
    }
}
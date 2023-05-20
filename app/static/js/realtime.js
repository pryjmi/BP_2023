var load = window.addEventListener
load("load", display_time)
load("load", display_realtime)

function display_realtime() {
    var refresh = 1000;
    mytime = setTimeout("display_time()", refresh);
}
function display_time() {
    var date = new Date();

    var hours = date.getHours().toString();
    hours=hours.toString().length==1? 0+hours.toString() : hours;

    var minutes = date.getMinutes().toString();
    minutes=minutes.length==1 ? 0+minutes : minutes;

    var seconds = date.getSeconds().toString();
    seconds=seconds.length==1 ? 0+seconds : seconds;

    var current_time = hours+":"+minutes+":"+ seconds;
    document.getElementById("time").innerHTML = current_time;

    display_realtime();
}
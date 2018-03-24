var sidebar = document.getElementById('sidebar');
var sidebarScroll = 0;
var lastScroll = 0;
var topMargin = sidebar.offsetTop;

sidebar.style.bottom = 'auto';

function update() {
    var delta = window.scrollY - lastScroll;
    sidebarScroll += delta;
    lastScroll = window.scrollY;

    if(sidebarScroll < 0) {
        sidebarScroll = 0;
    } else if(sidebarScroll > sidebar.scrollHeight - window.innerHeight + topMargin * 2) {
        sidebarScroll = sidebar.scrollHeight - window.innerHeight + topMargin * 2;
    }

    sidebar.style.marginTop = -sidebarScroll + 'px';
}

document.addEventListener('scroll', update);
window.addEventListener('resize', update);
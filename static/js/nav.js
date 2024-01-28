

window.onresize = function() {
  var menu_open_btn = document.getElementById("menu");
  var menu_close_btn = document.getElementById("close_menu");
  var menu_sidebar = document.getElementById("sidebar");

  if( menu_open_btn && menu_close_btn && menu_sidebar){
    if( window.innerWidth > 600  ){
        menu_open_btn.style.display="none";
        menu_sidebar.style.display = "block";
    }
    else{
      menu_open_btn.style.display="block";
      menu_sidebar.style.display = "none";
    }
    menu_close_btn.style.display="none";
  }
};



function show_menu(){
  sidebar_helper("block");
}

function close_menu(){
  sidebar_helper("none");
}

function sidebar_helper( sidebar_display ) {

  var sidebar = document.getElementById("sidebar");
  var open_btn = document.getElementById("menu");
  var close_btn = document.getElementById("close_menu");
  var body = document.getElementById("base_body");

  if (sidebar) {
    sidebar.style.display = sidebar_display;
    close_btn.style.display = sidebar_display;

    open_btn.style.display = ( sidebar_display === "none" ) ? "block": "none";
    body.style.overflow = ( sidebar_display === "none" ) ? "auto": "hidden";
  }

}
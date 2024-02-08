

window.onresize = function() {
  var menu_open_btn = document.getElementById("menu");
  var menu_close_btn = document.getElementById("close_menu");
  var menu_sidebar = document.getElementById("sidebar");
  var sidebar_log_out = document.getElementById("log_out_container");

  if( menu_open_btn && menu_close_btn && menu_sidebar){
    if( window.innerWidth > 600  ){
        menu_open_btn.style.display="none";
        menu_sidebar.style.display = "block";
        // log_out_container.style.display = "none";
    }
    else{
      menu_open_btn.style.display="block";
      // menu_sidebar.style.display = "none";
      // log_out_container.style.display = "block";
    }
    menu_close_btn.style.display="none";
  }
};

// Get the container element
var ul = document.getElementById("list_container");

// Get all buttons with class="btn" inside the container
var btns = ul.getElementsByClassName("sidebar_btns");

// Loop through the buttons and add the active_tab class to the current/clicked button
for (var i = 0; i < btns.length; i++) {
  btns[i].addEventListener("click", function() {
    var current = ul.getElementsByClassName("active_tab");
    current[0].className = current[0].className.replace(" active_tab", "");
    this.className += " active_tab";
  });
}


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

function expandSidebar(){
  var list_btn = document.getElementById("expand_sidebar");
  var colapse_btn = document.getElementById("colapse_sidebar");
  var ul = document.getElementById("list_container");

  // user if sidebar will display icons only, initially
  var sidebar_list_text = document.getElementsByClassName( "sidebar_list_text" );

  if ( list_btn && colapse_btn && ul ){
    // to expand sidebar
    if( list_btn.style.display  === "block" ){
      list_btn.style.display =  "none";
      colapse_btn.style.display =  "block";
      for( var i=0; i<sidebar_list_text.length;i++ ){
        sidebar_list_text[i].style.display = "inline";
      }
      // ul.style.display = "block";
      // ul.style.opacity = "1";
    }
    // to colapse sidebar
    else{
      list_btn.style.display =  "block";
      colapse_btn.style.display =  "none";
      for( var i=0; i<sidebar_list_text.length;i++ ){
        sidebar_list_text[i].style.display = "none";
      }
      // ul.style.display = "none";
      // ul.style.opacity = "0";
    }
  }
}

function assign_active( btn_id ){
  var container = document.getElementById("list_container");
  var li_arr = container.getElementsByTagName("li");
  
  for (var i=0;i<li_arr.length;i++){
    var btn = li_arr[i].getElementsByTagName("a");
    console.log(btn.className);
    if( btn.className == " active_tab"){

    }
  }


  // set tab  as active and remove all other classes
  // document.getElementById( btn_id ).className  += " active_tab";

}



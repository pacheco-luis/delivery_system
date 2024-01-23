
function show_menu(){
  var sidebar = document.getElementById("sidebar");
  var close_ele = document.getElementById("close_menu");

  if (sidebar) {
    var currentDisplay = window.getComputedStyle(sidebar).getPropertyValue('display');
    sidebar.style.display = 'block';
  }

  if( close_ele ){
    var menu = document.getElementById("menu");
    if( menu ){
      menu.style.display = 'none';
    }

    close_ele.style.display = 'block';
  }
}

function close_menu(){
  var sidebar = document.getElementById("sidebar");
  var menu_btn = document.getElementById("menu");

  if (sidebar) {
    var currentDisplay = window.getComputedStyle(sidebar).getPropertyValue('display');
    sidebar.style.display = 'none';
  }

  if( menu_btn ){
    var close_menu = document.getElementById("close_menu");
    if( close_menu ){
      close_menu.style.display = 'none';
    }

    menu_btn.style.display = 'block';
  }
}
function show_pwd(){
    var pwd_element = document.getElementById("password_input");

    if( pwd_element.type === "password" ){
        pwd_element.type = "text";
    }
    else{
        pwd_element.type = "password";
    }

}
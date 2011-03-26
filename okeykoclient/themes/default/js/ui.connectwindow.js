function connectWindowSettings() {
    $("#LoginWindow > .body > .button").click(function() {
        sendLogin();
    });
    $("#LoginWindow > .body :input").eq(0).autocomplete({source: []})
    $("#LoginWindow > .body :input").eq(0).bind("autocompleteselect", LoginAutoCompleteCB);
    alert("okeyko:LoginAutoComplete");
    $("#LoginWindow > .body :input[type='checkbox']").each(function (index) {
        function setValue(check) {
            if( $(check).is(":checked")) {
                $(check).val(true);
            }
            else {
                $(check).val(false);
            }
        }
        function activate(check) {
            if(! $(check).is(":checked")) {
                $(check).click();
            }
        }        
        setValue($(this));
        $(this).click(function() {setValue($(this))});
        if (index >= 1) {
            $(this).click(function() {activate($("#LoginWindow > .body :input[type='checkbox']")[0])});
        }
        if (index >= 2) {
            $(this).attr("disabled","disabled");
            $(this).click(function() {activate($("#LoginWindow > .body :input[type='checkbox']")[1])});
        }
    });
        
}

function LoginAutoComplete(SourceArray) {
    $("#LoginWindow > .body :input").eq(0).autocomplete("option", "source", SourceArray);
}

function LoginAutoCompleteCB(event, ui) {
    alert("okeyko:LoginAutoComplete:Complete:"+$(ui.item).val());
}
function LoginAutoCompleteCBPy(img, pass) {
    var imgshow = $("#LoginWindow > .body >.avatar > img").not(".opaque");
    $(imgshow).attr('src', "file://"+img);

    $("#LoginWindow > .body > .avatar > img").removeClass("opaque");
    $(imgshow).addClass("opaque");
    $("#LoginWindow > .body :input[type='checkbox']").eq(0).not(":checked").click().val(true);
    if (pass){
        $("#LoginWindow > .body :input[type='checkbox']").eq(1).not(":checked").click().val(true);
        $("#LoginWindow > .body :input").eq(1).val(pass);
    }
    else {
        $("#LoginWindow > .body :input[type='checkbox']").eq(1).is(":checked").click().val(false);
        $("#LoginWindow > .body :input").eq(1).val('');
    }
}

function sendLogin() {
    var alertText = '';
    var logi = $("#LoginWindow > .body :input").each(function() {
        if (! $(this).val() ) {
            $(this).css('background-color', 'red');
            alertText = false
            return false;
        }
        alertText = alertText + $(this).val() + "|" ;
    });
    if (! alertText) {
        alert('error');
    }
    else {
        alert('okeyko:login:' + alertText);
        LoadingConnect();
    }
}

function LoadingConnect() {
    $('#ModalBg').show();
    $('#LoadingConnect').show();
}

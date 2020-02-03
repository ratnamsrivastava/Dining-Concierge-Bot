//links
//http://eloquentjavascript.net/09_regexp.html
//https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_Expressions


var messages = [], //array that hold the record of each string in chat
  lastUserMessage = "", //keeps track of the most recent input string from the user
  botMessage = "", //var keeps track of what the chatbot is going to say
  botName = 'DiningBot', //name of the chatbot
  talking = true; //when false the speach function doesn't work
//
//
//****************************************************************
//****************************************************************
//****************************************************************
//****************************************************************
//****************************************************************
//****************************************************************
//****************************************************************
//edit this function to change what the chatbot says

var MODE = "PROD"


$("#btnInput").keypress(function (event) {
    if (event.keyCode == 13) {
        let userText = $("#btnInput").val()
        var params = {};
        var additionalParams = {};

        var body = {
                    "messages" : [ {
                        "type": "User Testing",
                        "unstructured": {
                            "id":"1",
                            "text": userText,
                            "timestamp":"2019"
                        }
                    }
                    ]
        };
        document.getElementById("cnt1").value += 'User: '+ userText + '\n';
        // $("#cnt1").html("User: "+$("#btnInput").val()+"\n").css("font-weight", "Bold")
        $("#btnInput").val("")
        apigClient.chatbotPost(params,body,additionalParams)
            .then(function(result){
                // document.getElementById('out').innerHtml = result.data;
                console.log(result)
                document.getElementById("cnt1").value += 'Bot: ' + result["data"]["200"]["BotResponse"]["messages"][0]["unstructured"]["text"] + '\n'+'\n';
                // document.getElementById('out').innerHtml.append(result.data);
                
            }).catch( function(result){
            
            });
        
    };
});
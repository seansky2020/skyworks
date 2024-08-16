let lastMessage = '';

function sendMessage() {
    var userInput = $('#user-input').val();
    if (userInput.trim() === '') return;

    // Store the last message
    lastMessage = userInput;

    $('#chat-box').append('<p><strong>You:</strong> ' + userInput + '</p>');
    $('#user-input').val('');

    $.ajax({
        url: '/chat',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({message: userInput}),
        success: function(response) {
            $('#chat-box').append('<p><strong>Agent:</strong> ' + response.response + '</p>');
            $('#chat-box').scrollTop($('#chat-box')[0].scrollHeight);
        }
    });
}

function retryLastMessage() {
    if (lastMessage) {
        $('#user-input').val(lastMessage);
        sendMessage();
    }
}

function undoLastMessage() {
    var chatBox = $('#chat-box');
    var messages = chatBox.find('p');

    if (messages.length >= 2) {
        messages.last().remove(); // Remove the agent's response
        messages.last().remove(); // Remove the user's message
    }
}

$('#user-input').keypress(function(e) {
    if (e.which == 13) {
        sendMessage();
        return false;
    }
});

function clearChat() {
    $('#chat-box').empty();
    lastMessage = '';  // Reset the lastMessage variable when clearing the chat
}

function useExample(element) {
    $('#user-input').val($(element).text());
}

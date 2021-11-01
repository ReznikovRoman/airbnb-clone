"use strict";


const realtyTypeBtn = $('#realty-type--btn');
const realtyTypeForm = realtyTypeBtn.siblings('form');
const realtyFiltersBtn = $('#realty-filters-all--btn');

const overlayEl = $('.overlay');
const popupEl = $('.filter-popup');
const closePopupEl = $('.close-popup');


realtyTypeForm.click(function (e) {
    e.stopPropagation();
});

$('body').click(function () {
    if (!realtyTypeForm.hasClass('hidden')) realtyTypeForm.toggleClass('hidden');
});


function closePopup() {
    popupEl.toggleClass('hidden');
    overlayEl.addClass('hidden');
    $('html, body').css({
        overflow: 'auto',
        height: 'auto'
    });
}

document.addEventListener(
    'keydown',
    function (event) {
        if (event.key === 'Escape') {
            if (!popupEl.hasClass('hidden')) {
                closePopup();
            }
            if (!realtyTypeForm.hasClass('hidden')) {
                realtyTypeForm.toggleClass('hidden');
            }
        }
    }
);
closePopupEl.click(closePopup);
overlayEl.click(closePopup);

realtyFiltersBtn.click(
    function () {
        popupEl.toggleClass('hidden');
        overlayEl.toggleClass('hidden');
        $('html, body').css({
            overflow: 'hidden',
            height: '100%'
        });
    }
);


// Custom number input (add and subtract buttons)
const customNumberInputs = $('.input-number--custom-field');
customNumberInputs.each(function () {
    $(this).wrap('<div class="input-number--custom-wrapper"></div>');
    $(this).parent().parent().addClass('flex--between');

    $(this).before('<button class="input-number--subtract" type="button">-</button>');
    $(this).after('<button class="input-number--add" type="button">+</button>');
});

const realtyFilterButtonsSubtract = $('.input-number--subtract');
const realtyFilterButtonsAdd = $('.input-number--add');
const realtyFilterInputs = $('.input-number--custom-wrapper input');

function getInputDataFromContext(context) {
    const inputEl = $(context).siblings('input');
    return {
        element: inputEl,
        value: parseInt(inputEl.val()),
        minValue: inputEl.attr('min'),
        maxValue: inputEl.attr('max'),
    };
}

realtyFilterButtonsSubtract.each(function () {
    $(this).click(function () {
        console.log("clicked");
        const inputData = getInputDataFromContext($(this));
        const inputValue = inputData["value"];

        if (inputValue - 1 > inputData["minValue"] - 1) {
            inputData["element"].val(inputValue - 1);
        }
    });
});
realtyFilterButtonsAdd.each(function () {
    $(this).click(function () {
        console.log("clicked");
        const inputData = getInputDataFromContext($(this));
        const inputValue = inputData["value"];

        if (inputValue + 1 <= inputData["maxValue"]) {
            inputData["element"].val(inputValue + 1);
        }
    });
});
realtyFilterInputs.each(function () {
    $(this).keypress(function (e) {
        return false;
    });
});


// Live chat
$('#live-chat header').on('click', function() {
    $('.chat').slideToggle(300, 'swing');
    $input.focus();
});

const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
const url = `${ws_scheme}://${window.location.host}/ws/chat-bot/`;

const chatSocket = new ReconnectingWebSocket(url);

const $input = $('#chat-bot-message-input');
const $submit = $('#chat-bot-message-submit');

const $chat = $('.chat-history');

$chat.scrollTop($chat[0].scrollHeight);

$submit.click(function () {
    const message = $input.val();
    if (message) {
        // send message in a JSON format
        chatSocket.send(JSON.stringify({'message': message}));

        // clear input
        $input.val('');
    }
});

chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    const message = data.message;

    const dateOptions = {hour: 'numeric', minute: 'numeric', hour12: true};
    const datetime = new Date(data['datetime']).toLocaleString('en', dateOptions);

    const isMessageFromUser = data.is_message_from_user;

    if (isMessageFromUser) {
        $chat.append(
            `<div class="chat-message message-user">
                <div class="chat-message-content">
                    <span class="chat-time">${datetime}</span>
                    <p>${message}</p>
                </div>
             </div>`
        );
    } else {
        $chat.append(
            `<div class="chat-message message-bot">
                <div class="chat-message-content">
                    <span class="chat-time">${datetime}</span>
                    <h5>Air Helper</h5>
                    <p>${message}</p>
                </div>
             </div>`
        );
    }
    $chat.scrollTop($chat[0].scrollHeight);
};

chatSocket.onclose = function (e) {
    console.error('Chat socket closed unexpectedly');
};

$input.keyup(function (e) {
    if (e.which === 13) {
        // submit with enter/return key
        $submit.click();
    }
});

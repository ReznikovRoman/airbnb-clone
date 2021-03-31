"use strict";


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
        const inputData = getInputDataFromContext($(this));
        const inputValue = inputData["value"];

        if (inputValue - 1 > inputData["minValue"] - 1) inputData["element"].val(inputValue - 1);
    });
});
realtyFilterButtonsAdd.each(function () {
    $(this).click(function () {
        const inputData = getInputDataFromContext($(this));
        const inputValue = inputData["value"];

        if (inputValue + 1 <= inputData["maxValue"]) inputData["element"].val(inputValue + 1);
    });
});
realtyFilterInputs.each(function () {
    $(this).keypress(function (e) {
        return false;
    });
});

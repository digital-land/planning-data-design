(function () {
  'use strict';

  const utils = {};

  utils.createTypeAheadContainer = function (labelText, id) {
    // create a label element
    const $label = document.createElement('label');
    $label.classList.add('govuk-label');
    $label.htmlFor = id + '-typeAhead';
    $label.textContent = labelText;

    // create the autocomplete container
    const $autocompleteContainer = document.createElement('div');
    $autocompleteContainer.classList.add('autocomplete-container');
    // this.$autocompleteContainer.id = 'my-autocomplete-container'

    // create form-group
    const $formGroup = document.createElement('div');
    $formGroup.classList.add('govuk-form-group');

    $formGroup.appendChild($label);
    $formGroup.appendChild($autocompleteContainer);

    return $formGroup
  };

  utils.getSelectOptions = function ($select) {
    const $options = $select.querySelectorAll('option');
    return Array.from($options).map(($option) => [$option.textContent, $option.value])
  };

  utils.postToBackend = function (url, data, onSuccess, onError) {
    fetch(url, {
      method: 'POST',
      body: JSON.stringify(data),
      headers: {
        'Content-Type': 'application/json'
      }
    })
      .then(response => response.json())
      .then(data => {
        if (onSuccess) {
          onSuccess(data);
        } else {
          console.log('Success:', data);
        }
      })
      .catch((error) => {
        if (onError) {
          onError(error);
        } else {
          console.error('Error:', error);
        }
      });
  };

  /* global accessibleAutocomplete */

  function SelectOrNew ($selectContainer, selectId, templateId) {
    this.$selectContainer = $selectContainer;
    this.selectId = selectId;
    this.templateId = templateId;
  }

  SelectOrNew.prototype.init = function () {
    this.$selectFormGroup = this.$selectContainer.querySelector('.govuk-form-group');
    this.$select = document.getElementById(this.selectId);
    this.$label = this.$selectFormGroup.querySelector('label');

    this.typeAheadId = this.selectId + '-typeAhead';
    //this.selectOptionList = this.getSelectOptions()
    this.getSelectOptions();
    //this.currentOptions = this.orginalOptions
    this.$actionPanelTemplate = document.getElementById(this.templateId);

    this.newRecordName = '';
    // gets updated when user confirm or blur has happened
    this.lastInputValue = '';

    // hide original select group
    this.$selectFormGroup.classList.add('govuk-visually-hidden');

    // insert action panel first so that can use insertBefore for typeahead
    this.$actionPanel = this.setUpActionPanel();
    this.setUpTypeAhead();
  };

  SelectOrNew.prototype.autoCompleteOnConfirm = function (e) {
    const inputValue = this.$typeAheadInput.value;
    this.lastInputValue = inputValue;
    // const $input = this.$autocompleteContainer.querySelector('.autocomplete__wrapper input')
    // when user clicks on option e is set to value
    if (this.selectOptionList.includes(e) || this.selectOptionList.includes(inputValue)) {
      // value exists so set select to this option
      console.log('existing value');
      const optLabel = e || inputValue;
      const selectedOption = this.getSelectedOption(optLabel);
      this.selectOption(selectedOption[0][1]);
    } else {
      if (inputValue !== '') {
        //this.newRecordName = this.$typeAheadInput.value
        console.log(this.lastInputValue);
        this.showRequestAction(this.lastInputValue);
      }
    }
  };

  SelectOrNew.prototype.createTypeAheadContainer = function (labelText) {
    // create a label element
    const $label = document.createElement('label');
    $label.classList.add('govuk-label');
    $label.htmlFor = this.typeAheadId;
    $label.textContent = labelText;

    // create the autocomplete container
    this.$autocompleteContainer = document.createElement('div');
    // this.$autocompleteContainer.id = 'my-autocomplete-container'

    // create form-group
    const $formGroup = document.createElement('div');
    $formGroup.classList.add('govuk-form-group');

    $formGroup.appendChild($label);
    $formGroup.appendChild(this.$autocompleteContainer);

    return $formGroup
  };

  SelectOrNew.prototype.getSelectedOption = function (label) {
    console.log('label', label);
    return this.selectOptions.filter(opt => opt[0] === label)
  };

  SelectOrNew.prototype.getSelectOptions = function () {
    const $options = this.$select.querySelectorAll('option');
    this.selectOptions = Array.from($options).map(($option) => [$option.textContent, $option.value]);
    this.selectOptionList = this.selectOptions.map(($option) => $option[0]);
    //return Array.from($options).map(($option) => $option.textContent)
  };

  SelectOrNew.prototype.hideActionPanel = function () {
    this.$actionPanel.classList.remove('new-tag__mode--request');
    this.$actionPanel.classList.remove('new-tag__mode--result');
  };

  SelectOrNew.prototype.initAccessibleAutocomplete = function () {
    const boundAutoCompleteOnConfirm = this.autoCompleteOnConfirm.bind(this);
    console.log('setup', this.selectOptionList);
    accessibleAutocomplete({
      element: this.$autocompleteContainer,
      id: this.typeAheadId, // To match it to the existing <label>.
      source: this.selectOptionList,
      showNoOptionsFound: false,
      defaultValue: this.lastInputValue,
      onConfirm: boundAutoCompleteOnConfirm
    });

    // store reference to input
    this.$typeAheadInput = this.$typeAheadContainer.querySelector('.autocomplete__wrapper input');
    const boundOnReenterInput = this.onReenterInput.bind(this);
    this.$typeAheadInput.addEventListener('focus', boundOnReenterInput);
  };

  SelectOrNew.prototype.onConfirmRequest = function (e) {
    e.preventDefault();
    console.log('ajax request to create new event', e);
    console.log(this.$actionPanel.classList);

    this.postNewTag();
  };

  SelectOrNew.prototype.onReenterInput = function (e) {
    //this.newRecordName = ''
    this.hideActionPanel();
  };

  SelectOrNew.prototype.postNewTag = function () {
    const tag = {
      name: this.lastInputValue,
    };
    const boundPostNewTagSuccess = this.postNewTagSuccess.bind(this);
    utils.postToBackend(
      '/tags/add-ajax', tag, boundPostNewTagSuccess
    );
  };

  SelectOrNew.prototype.postNewTagSuccess = function (data) {
    this.showResultPanel();
    const newTag = data.tag;
    this.updateSelect(newTag.name, newTag.id);
  };

  SelectOrNew.prototype.selectOption = function (val) {
    this.$select.value = val;
  };

  SelectOrNew.prototype.setUpActionPanel = function () {
    const $actionPanelFrag = this.$actionPanelTemplate.content.cloneNode(true);
    this.$selectContainer.appendChild($actionPanelFrag);
    return this.$selectContainer.querySelector('.app-action-panel')
  };

  SelectOrNew.prototype.setUpTypeAhead = function () {
    const labelText = this.$label.textContent;
    this.$typeAheadContainer = this.createTypeAheadContainer(labelText);
    this.$selectContainer.insertBefore(this.$typeAheadContainer, this.$actionPanel);

    this.initAccessibleAutocomplete();
  };

  SelectOrNew.prototype.showRequestAction = function (val) {
    const $nameEls = this.$actionPanel.querySelectorAll('[data-new-tag="name"]');
    $nameEls.forEach(function ($el) { $el.textContent = val; });

    const $confirmBtn = this.$actionPanel.querySelector('[data-new-tag="request"] button');
    const boundOnConfirmRequest = this.onConfirmRequest.bind(this);
    $confirmBtn.addEventListener('click', boundOnConfirmRequest);

    this.$actionPanel.classList.remove('new-tag__mode--result');
    this.$actionPanel.classList.add('new-tag__mode--request');
  };

  SelectOrNew.prototype.showResultPanel = function () {
    this.$actionPanel.classList.remove('new-tag__mode--request');
    this.$actionPanel.classList.add('new-tag__mode--result');
  };

  SelectOrNew.prototype.updateSelect = function (name, val) {
    console.log('updating select');
    // check element hasn't already been added
    if (!this.$select.querySelector(`[value="${val}"]`)) {
      this.$select.append(this.createOptionElement(name, val));
      this.selectOption(val);
      this.getSelectOptions();
      this.updateSources();
    }
  };

  SelectOrNew.prototype.createOptionElement = function (name, val) {
    // Create a new option element
    const $option = document.createElement('option');
    $option.value = val;
    $option.textContent = name;
    return $option
  };

  SelectOrNew.prototype.updateSources = function () {
    // replace typeahead
    this.$typeAheadContainer.remove();
    this.setUpTypeAhead();
  };

  /* global accessibleAutocomplete */

  function MultiSelect ($module) {
    this.$module = $module;
  }

  MultiSelect.prototype.init = function (params) {
    this.setupOptions(params);
    // get the original form field that needs to be kept updated
    this.$formGroup = this.$module.querySelector('[data-multi-select="form-group"]');
    this.$input = this.$formGroup.querySelector('input');

    // get the options from a hidden select element
    this.$hiddenSelect = this.$module.querySelector('[data-multi-select="select"]');
    this.selectOptions = utils.getSelectOptions(this.$hiddenSelect);
    this.selectOptionLabels = this.selectOptions.map(($option) => $option[0]);

    // get the initial set of selections from existing input
    this.currentlySelected = [];
    this.initiallySelected();

    // set up a type ahead component
    this.setUpTypeAhead();
    // setup area to display selected
    this.setupSelectedPanel();

    // hide the original form element
    this.$formGroup.classList.add(this.options.hiddenClass);

    return this
  };

  MultiSelect.prototype.autoCompleteOnConfirm = function (inputValue) {
    if (inputValue) {
      // First try to find a matching option
      const option = this.findOption(inputValue, 'name');

      if (option.length) {
        // Existing behavior for matching options
        if (!this.currentlySelected.includes(option[0][1])) {
          this.currentlySelected.push(option[0][1]);
          this.displaySelectedItem(option[0]);
        }
      } else {
        // New behavior: Allow non-matching values
        const newOption = [inputValue, inputValue];

        // Check against display value (first element) to prevent duplicates
        const isDuplicate = this.currentlySelected.some(selected => {
          const existingOption = this.findOption(selected, 'value');
          return existingOption.length ?
            existingOption[0][0].toLowerCase() === inputValue.toLowerCase() :
            selected.toLowerCase() === inputValue.toLowerCase()
        });

        if (!isDuplicate) {
          this.currentlySelected.push(inputValue);
          this.displaySelectedItem(newOption);
        }
      }

      // Update the original input
      this.updateInput();

      // Clear the typeahead input if option set
      if (this.options.emptyInputOnConfirm) {
        const $typeAheadInput = this.$typeAheadContainer.querySelector('.autocomplete__input');
        setTimeout(function () {
          $typeAheadInput.value = '';
        }, 150);
      }
    }
  };

  MultiSelect.prototype.createSelectedItem = function (optionPair) {
    const $item = document.createElement('li');
    const $content = document.createElement('div');
    const $label = document.createElement('span');
    $label.classList.add(this.options.selectedClass);
    $label.textContent = optionPair[0];

    const $val = document.createElement('span');
    $val.classList.add('multi-select__item-value');
    $val.textContent = optionPair[1];

    // Only show value if it's a UUID (existing tag)
    if (!this.isUUID(optionPair[1])) {
      $val.style.display = 'none';
    }

    const $cancelBtn = document.createElement('a');
    $cancelBtn.classList.add('govuk-link');
    $cancelBtn.classList.add('app-destructive-link');
    $cancelBtn.textContent = 'remove';
    $cancelBtn.href = '#';
    const boundOnDeselectItem = this.onDeselectItem.bind(this);
    $cancelBtn.addEventListener('click', boundOnDeselectItem);

    $content.appendChild($label);
    $content.appendChild($val);

    $item.appendChild($content);
    $item.appendChild($cancelBtn);
    return $item
  };

  MultiSelect.prototype.onDeselectItem = function (e) {
    e.preventDefault();
    const $deselectBtn = e.currentTarget;
    const $item = $deselectBtn.closest('li');
    const $label = $item.querySelector('.' + this.options.selectedClass);
    const $val = $item.querySelector('.multi-select__item-value');

    // Use the value if it's a UUID (existing tag), otherwise use the label (new tag)
    const valueToRemove = $val.style.display === 'none' ? $label.textContent : $val.textContent;

    $item.remove();
    this.currentlySelected = this.currentlySelected.filter(item => item !== valueToRemove);
    this.updateInput();
    this.updatePanelContent();
  };

  MultiSelect.prototype.createSelectedPanel = function () {

    const $panel = document.createElement('div');
    $panel.classList.add('multi-select__select-panel');

    const $heading = document.createElement('h4');
    $heading.classList.add('govuk-heading-s');
    $heading.textContent = `Selected ${this.options.nameOfThingSelecting}`;
    const $selectedList = document.createElement('ul');

    const $noSelectionText = document.createElement('p');
    $noSelectionText.classList.add('govuk-hint');
    $noSelectionText.textContent = 'No selections made';

    $panel.append($heading);
    $panel.append($selectedList);
    $panel.append($noSelectionText);
    return $panel
  };

  MultiSelect.prototype.displaySelected = function () {
    if (this.currentlySelected.length) {
      this.currentlySelected.forEach(function (selection) {
        const option = this.findOption(selection, 'value');
        this.displaySelectedItem(option[0]);
      }.bind(this));
    }
    this.updatePanelContent();
  };

  MultiSelect.prototype.displaySelectedItem = function (option) {
    const $list = this.$selectedPanel.querySelector('ul');
    $list.append(this.createSelectedItem(option));
    this.updatePanelContent();
  };

  MultiSelect.prototype.findOption = function (query, _type) {
    const tupleIndx = (_type === 'value') ? 1 : 0;
    return this.selectOptions.filter(opt => opt[tupleIndx] === query)
  };

  MultiSelect.prototype.getSelectionsFromString = function (str) {
    const selections = str.split(this.options.separator);
    return selections.filter(s => s !== '')
  };

  MultiSelect.prototype.initAccessibleAutocomplete = function ($container) {
    const boundAutoCompleteOnConfirm = this.autoCompleteOnConfirm.bind(this);
    accessibleAutocomplete({
      element: $container.querySelector('.autocomplete-container'),
      id: $container.querySelector('label').htmlFor,
      source: this.selectOptionLabels,
      showNoOptionsFound: true,
      onConfirm: boundAutoCompleteOnConfirm,
    });
  };

  MultiSelect.prototype.initiallySelected = function () {
    const inputString = this.$input.value;
    this.currentlySelected = this.getSelectionsFromString(inputString);
  };

  MultiSelect.prototype.setupSelectedPanel = function () {
    this.$selectedPanel = this.createSelectedPanel();
    this.$module.append(this.$selectedPanel);
    this.displaySelected();
  };

  MultiSelect.prototype.setUpTypeAhead = function () {
    const labelText = this.$formGroup.querySelector('label').textContent;
    this.$typeAheadContainer = utils.createTypeAheadContainer(labelText, this.$hiddenSelect.id);
    this.$module.append(this.$typeAheadContainer);

    this.initAccessibleAutocomplete(this.$typeAheadContainer);
    this.$typeAheadInput = this.$typeAheadContainer.querySelector('.autocomplete__input');
  };

  // this keeps the hidden input updated
  // ... existing code ...
  MultiSelect.prototype.updateInput = function () {
    if (this.currentlySelected.length === 0) {
      this.$input.value = '';
    } else {
      // Join all selected values with the separator
      this.$input.value = this.currentlySelected.join(this.options.separator);
    }
  };

  // ... rest of existing code ...

  MultiSelect.prototype.updatePanelContent = function () {
    // if no items selected then show no selection msg
    if (this.currentlySelected.length > 0) {
      this.$selectedPanel.classList.remove('multi-select__select-panel--none');
      this.$selectedPanel.classList.add('multi-select__select-panel--selection');
    } else {
      this.$selectedPanel.classList.add('multi-select__select-panel--none');
      this.$selectedPanel.classList.remove('multi-select__select-panel--selection');
    }
  };

  MultiSelect.prototype.setupOptions = function (params) {
    params = params || {};
    this.options = {};
    this.options.separator = params.separator || ';';
    this.options.nameOfThingSelecting = params.nameOfThingSelecting || 'tags';
    this.options.hiddenClass = params.hiddenClass || 'app-hidden';
    this.options.emptyInputOnConfirm = params.emptyInputOnConfirm || true;
    this.options.selectedClass = params.selectedClass || 'multi-select__item-label';
  };

  // Add a helper method to check if a string is a UUID
  MultiSelect.prototype.isUUID = function (str) {
    const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    return uuidPattern.test(str)
  };

  /* global fetch, turf */

  window.dptp = {
    SelectOrNew: SelectOrNew,
    MultiSelect: MultiSelect,
  };

})();

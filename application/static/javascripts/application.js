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

  window.dptp = {
    MultiSelect: MultiSelect,
  };

})();

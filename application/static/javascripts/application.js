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

  SelectOrNew.prototype.init = function (params) {
    params = params || {};
    this.options = {};
    this.options.new_backend_endpoint = params.new_backend_endpoint || false;
    this.$selectFormGroup = this.$selectContainer.querySelector('.govuk-form-group');
    this.$select = document.getElementById(this.selectId);
    this.$label = this.$selectFormGroup.querySelector('label');
    this.$form = this.$selectContainer.closest('form');

    this.typeAheadId = this.selectId + '-typeAhead';
    this.getSelectOptions();
    this.$actionPanelTemplate = document.getElementById(this.templateId);

    this.newRecordName = '';
    this.lastInputValue = '';

    // hide original select group
    this.$selectFormGroup.classList.add('govuk-visually-hidden');

    // insert action panel first so that can use insertBefore for typeahead
    this.$actionPanel = this.setUpActionPanel();
    this.setUpTypeAhead();

    // Prevent form submission when confirmation panel is shown
    if (this.$form) {
      this.$form.addEventListener('submit', (e) => {
        if (this.$actionPanel.classList.contains('new-tag__mode--request')) {
          e.preventDefault();
        }
      });
    }
  };

  SelectOrNew.prototype.autoCompleteOnConfirm = function (e) {
    const inputValue = this.$typeAheadInput.value.trim();
    this.lastInputValue = inputValue;

    if (inputValue === '') {
      return
    }

    // when user clicks on option e is set to value
    if (this.selectOptionList.includes(e) || this.selectOptionList.includes(inputValue)) {
      // value exists so set select to this option
      const optLabel = e || inputValue;
      const selectedOption = this.getSelectedOption(optLabel);
      this.selectOption(selectedOption[0][1]);
    } else {
      // Handle non-matching input value - same flow as blur
      this.showRequestAction(inputValue);
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
    if (this.options.new_backend_endpoint) {
      utils.postToBackend(
        this.options.new_backend_endpoint, tag, boundPostNewTagSuccess
      );
    } else {
      console.log('no new backend endpoint');
    }
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

    // Handle enter key for input, confirmation panel, and form submission
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();

        // If confirmation panel is showing, handle "Yes, add it" action
        if (this.$actionPanel.classList.contains('new-tag__mode--request')) {
          this.onConfirmRequest(e);
          return
        }

        // If result panel is showing, submit the form
        if (this.$actionPanel.classList.contains('new-tag__mode--result')) {
          this.$form.submit();
          return
        }

        // Otherwise handle the input value
        const inputValue = this.$typeAheadInput.value.trim();
        if (inputValue === '') {
          return
        }

        if (!this.selectOptionList.includes(inputValue)) {
          // Show the confirmation panel for new tags
          this.lastInputValue = inputValue;
          this.showRequestAction(inputValue);
        }
      }
    });
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

  /* global accessibleAutocomplete */

  function MultiSelectOrNew($module) {
    this.$module = $module;
    this.selectedTags = [];
  }

  MultiSelectOrNew.prototype.init = function(params) {
    this.setupOptions(params);

    // Get elements
    this.$select = this.$module.querySelector('select');
    this.$selectedTagsContainer = this.$module.querySelector('.app-selected-tags');
    this.$selectedTagsInput = this.$module.querySelector('#selected-tags-input');
    this.$form = this.$module.closest('form');

    // Get initial options
    this.selectOptions = Array.from(this.$select.querySelectorAll('option')).map(($option) => ({
      text: $option.textContent,
      value: $option.value
    }));

    // Hide the original select
    this.$select.style.display = 'none';

    // Set up typeahead
    this.setupTypeahead();

    // Set up action panel for new tags
    this.$actionPanelTemplate = document.getElementById(this.options.actionPanelTemplateId);
    this.$actionPanel = this.setupActionPanel();

    // Initialize with any existing tags
    if (this.$selectedTagsInput.value) {
      const tagIds = this.$selectedTagsInput.value.split(',');
      tagIds.forEach(id => {
        const option = this.selectOptions.find(opt => opt.value === id);
        if (option) {
          this.addTag(option);
        }
      });
    }

    // Prevent form submission when confirmation panel is shown
    if (this.$form) {
      this.$form.addEventListener('submit', (e) => {
        if (this.$actionPanel.classList.contains('new-tag__mode--request')) {
          e.preventDefault();
        }
      });
    }

    return this
  };

  MultiSelectOrNew.prototype.setupOptions = function(params) {
    params = params || {};
    this.options = {
      actionPanelTemplateId: params.actionPanelTemplateId || 'action-panel-template',
      newTagEndpoint: params.newTagEndpoint || false
    };
  };

  MultiSelectOrNew.prototype.setupTypeahead = function() {
    // Create typeahead container
    const $container = document.createElement('div');
    $container.classList.add('govuk-form-group');

    const $autocomplete = document.createElement('div');
    $container.appendChild($autocomplete);

    // Find the form group that contains the select
    const $formGroup = this.$module.querySelector('#new-tag-form-group');

    // Insert after the existing label
    const $existingLabel = $formGroup.querySelector('label');
    $formGroup.insertBefore($container, $existingLabel.nextSibling);

    // Initialize accessible autocomplete
    accessibleAutocomplete({
      element: $autocomplete,
      id: 'tag-typeahead',
      source: this.selectOptions.map(opt => opt.text),
      showNoOptionsFound: false,
      onConfirm: (inputValue) => this.handleTypeaheadConfirm(inputValue)
    });

    this.$typeaheadInput = $autocomplete.querySelector('input');
  };

  MultiSelectOrNew.prototype.handleTypeaheadConfirm = function(inputValue) {
    if (!inputValue) return

    const matchingOption = this.selectOptions.find(opt => opt.text === inputValue);

    if (matchingOption) {
      this.addTag(matchingOption);
    } else {
      this.showNewTagConfirmation(inputValue);
    }

    // Clear the input
    setTimeout(() => {
      this.$typeaheadInput.value = '';
    }, 150);
  };

  MultiSelectOrNew.prototype.addTag = function(tag) {
    if (!this.selectedTags.some(t => t.value === tag.value)) {
      this.selectedTags.push(tag);
      this.renderTags();
      this.updateHiddenInput();
    }
  };

  MultiSelectOrNew.prototype.removeTag = function(tagValue) {
    this.selectedTags = this.selectedTags.filter(tag => tag.value !== tagValue);
    this.renderTags();
    this.updateHiddenInput();
  };

  MultiSelectOrNew.prototype.renderTags = function() {
    const html = this.selectedTags.map(tag => `
    <span class="govuk-tag govuk-!-margin-right-1 govuk-!-margin-bottom-1">
      ${tag.text}
      <button type="button" class="app-tag-remove" data-value="${tag.value}" aria-label="Remove ${tag.text}">×</button>
    </span>
  `).join('');

    this.$selectedTagsContainer.innerHTML = html;

    // Add click handlers for remove buttons
    this.$selectedTagsContainer.querySelectorAll('.app-tag-remove').forEach(btn => {
      btn.onclick = () => this.removeTag(btn.dataset.value);
    });
  };

  MultiSelectOrNew.prototype.updateHiddenInput = function() {
    this.$selectedTagsInput.value = this.selectedTags.map(tag => tag.value).join(',');
  };

  MultiSelectOrNew.prototype.setupActionPanel = function() {
    const $panel = this.$actionPanelTemplate.content.cloneNode(true);
    this.$module.appendChild($panel);
    const $actionPanel = this.$module.querySelector('.app-action-panel');

    // Add click handler for confirm button
    const $confirmBtn = $actionPanel.querySelector('[data-new-tag="request"] button');
    $confirmBtn.addEventListener('click', (e) => this.handleNewTagConfirm(e));

    return $actionPanel
  };

  MultiSelectOrNew.prototype.showNewTagConfirmation = function(tagName) {
    const $nameEls = this.$actionPanel.querySelectorAll('[data-new-tag="name"]');
    $nameEls.forEach($el => { $el.textContent = tagName; });

    this.$actionPanel.classList.remove('new-tag__mode--result');
    this.$actionPanel.classList.add('new-tag__mode--request');

    this.pendingTagName = tagName;
  };

  MultiSelectOrNew.prototype.handleNewTagConfirm = function(e) {
    e.preventDefault();

    if (this.options.newTagEndpoint) {
      utils.postToBackend(
        this.options.newTagEndpoint,
        { name: this.pendingTagName },
        (data) => this.handleNewTagSuccess(data)
      );
    } else {
      console.warn('No new tag endpoint configured');
    }
  };

  MultiSelectOrNew.prototype.handleNewTagSuccess = function(data) {
    this.$actionPanel.classList.remove('new-tag__mode--request');
    this.$actionPanel.classList.add('new-tag__mode--result');

    const newTag = {
      text: data.tag.name,
      value: data.tag.id
    };

    // Add to options
    this.selectOptions.push(newTag);

    // Add new option to select
    const $option = document.createElement('option');
    $option.value = newTag.value;
    $option.textContent = newTag.text;
    this.$select.appendChild($option);

    // Add tag to selection
    this.addTag(newTag);
  };

  const cookieTypes = {
    cookies_policy: "essential",
    cookies_preferences_set: "essential",
    _ga: "usage",
    _gid: "usage",
    _gat: "usage",
  };

  // Initialize GA measurement ID cookie type if present
  if (typeof window !== 'undefined' && window.gaMeasurementId) {
    cookieTypes[`_ga_${window.gaMeasurementId}`] = 'usage';
  }

  function showCookieBannerIfNotSetAndSetTrackingCookies() {
    if(window.gaMeasurementId){
      cookieTypes[`_ga_${window.gaMeasurementId}`] = 'usage';
    }

    showCookieBanner();
    if (getCookie('cookies_preferences_set')) {
      hideCookieBanner();
    }

    setTrackingCookies();
  }

  function deleteCookie(name) {
    document.cookie = name + "=;expires=" + new Date + ";domain=" + window.location.hostname + ";path=/";
  }

  function setCookie(name, value, days) {
    var expires = '';
    if (days) {
      var date = new Date();
      date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
      expires = '; expires=' + date.toUTCString();
    }
    document.cookie = name + '=' + (value || '') + expires + '; path=/';
  }

  function getCookie(name) {
    var nameEQ = name + '=';
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
      var c = ca[i];
      while (c.charAt(0) === ' ') c = c.substring(1, c.length);
      if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length)
    }
    return null
  }

  function acceptCookies(cookiePrefs = { essential: true, settings: true, usage: true, campaigns: true }) { // eslint-disable-line no-unused-vars
    setCookie('cookies_preferences_set', true, 365);
    setCookie('cookies_policy', JSON.stringify(cookiePrefs), 365);
    hideCookieBanner();
    showCookieConfirmation();
    setTrackingCookies();
  }

  function hideCookieBanner() {
    var cookieBanner = document.getElementById('cookie-banner');
    if(cookieBanner){
      cookieBanner.style.display = 'none';
      cookieBanner.ariaHidden = true;
    }
  }

  function showCookieBanner() {
    var cookieBanner = document.getElementById('cookie-banner');
    if(cookieBanner){
      cookieBanner.style.display = 'block';
      cookieBanner.ariaHidden = false;
    }
  }

  function hideCookieConfirmation() {
    hideCookieBanner();
    var cookieBanner = document.getElementById('cookie-confirmation');
    if(cookieBanner){
      cookieBanner.style.display = 'none';
      cookieBanner.ariaHidden = true;
    }
  }

  function showCookieConfirmation() {
    var cookieBanner = document.getElementById('cookie-confirmation');
    if(cookieBanner){
      cookieBanner.style.display = 'block';
      cookieBanner.ariaHidden = false;
    }
  }

  function setTrackingCookies() {
    JSON.parse(getCookie('cookies_policy'));
    {
      if(window.gaMeasurementId){
        window[`ga-disable-${window.gaMeasurementId}`] = true;
      }
    }
  }

  class cookiePrefs {
    static essential = true;
    static settings = false;
    static usage = false;
    static campaigns = false;

    static get = () => {
      var cookiesPolicy = JSON.parse(getCookie('cookies_policy'));
      if(cookiesPolicy){
        this.setEssential(cookiesPolicy.essential);
        this.setSettings(cookiesPolicy.settings);
        this.setUsage(cookiesPolicy.usage);
        this.setCampaigns(cookiesPolicy.campaigns);
      }
    }

    static setEssential = (value) => this.essential = value;
    static setSettings = (value) => this.settings = value;
    static setUsage = (value) => this.usage = value;
    static setCampaigns = (value) => this.campaigns = value;

    static save = (expires = 365) => {
      setCookie('cookies_preferences_set', true, expires);
      setCookie('cookies_policy', JSON.stringify({
        essential: this.essential,
        settings: this.settings,
        usage: this.usage,
        campaigns: this.campaigns
      }), expires);
      hideCookieBanner();
      this.invalidateRejectedCookies();
      setTrackingCookies();
    }

    static invalidateRejectedCookies = () => {
      for (const name in cookieTypes){
        if(!this.essential && cookieTypes[name] == 'essential'){
          deleteCookie(name);
        }
        if(!this.settings && cookieTypes[name] == 'settings'){
          deleteCookie(name);
        }
        if(!this.usage && cookieTypes[name] == 'usage'){
          deleteCookie(name);
        }
        if(!this.campaigns && cookieTypes[name] == 'campaigns'){
          deleteCookie(name);
        }
      }
    }
  }

  var cookies = /*#__PURE__*/Object.freeze({
    __proto__: null,
    showCookieBannerIfNotSetAndSetTrackingCookies: showCookieBannerIfNotSetAndSetTrackingCookies,
    deleteCookie: deleteCookie,
    setCookie: setCookie,
    getCookie: getCookie,
    acceptCookies: acceptCookies,
    hideCookieBanner: hideCookieBanner,
    showCookieBanner: showCookieBanner,
    hideCookieConfirmation: hideCookieConfirmation,
    showCookieConfirmation: showCookieConfirmation,
    setTrackingCookies: setTrackingCookies,
    cookiePrefs: cookiePrefs
  });

  /* global fetch, turf */

  window.dptp = {
    SelectOrNew: SelectOrNew,
    MultiSelect: MultiSelect,
    MultiSelectOrNew: MultiSelectOrNew,
    cookies: cookies
  };

  // Initialize cookie banner when the module loads
  if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', function() {
      showCookieBannerIfNotSetAndSetTrackingCookies();
    });
  }

})();

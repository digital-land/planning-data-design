/* global accessibleAutocomplete */

import utils from './utils'

function SelectOrNew ($selectContainer, selectId, templateId) {
  this.$selectContainer = $selectContainer
  this.selectId = selectId
  this.templateId = templateId
}

SelectOrNew.prototype.init = function (params) {
  params = params || {}
  this.options = {}
  this.options.new_backend_endpoint = params.new_backend_endpoint || false
  this.$selectFormGroup = this.$selectContainer.querySelector('.govuk-form-group')
  this.$select = document.getElementById(this.selectId)
  this.$label = this.$selectFormGroup.querySelector('label')
  this.$form = this.$selectContainer.closest('form')

  this.typeAheadId = this.selectId + '-typeAhead'
  this.getSelectOptions()
  this.$actionPanelTemplate = document.getElementById(this.templateId)

  this.newRecordName = ''
  this.lastInputValue = ''

  // hide original select group
  this.$selectFormGroup.classList.add('govuk-visually-hidden')

  // insert action panel first so that can use insertBefore for typeahead
  this.$actionPanel = this.setUpActionPanel()
  this.setUpTypeAhead()

  // Prevent form submission when confirmation panel is shown
  if (this.$form) {
    this.$form.addEventListener('submit', (e) => {
      if (this.$actionPanel.classList.contains('new-tag__mode--request')) {
        e.preventDefault()
      }
    })
  }
}

SelectOrNew.prototype.autoCompleteOnConfirm = function (e) {
  const inputValue = this.$typeAheadInput.value.trim()
  this.lastInputValue = inputValue

  if (inputValue === '') {
    return
  }

  // when user clicks on option e is set to value
  if (this.selectOptionList.includes(e) || this.selectOptionList.includes(inputValue)) {
    // value exists so set select to this option
    const optLabel = e || inputValue
    const selectedOption = this.getSelectedOption(optLabel)
    this.selectOption(selectedOption[0][1])
  } else {
    // Handle non-matching input value - same flow as blur
    this.showRequestAction(inputValue)
  }
}

SelectOrNew.prototype.createTypeAheadContainer = function (labelText) {
  // create a label element
  const $label = document.createElement('label')
  $label.classList.add('govuk-label')
  $label.htmlFor = this.typeAheadId
  $label.textContent = labelText

  // create the autocomplete container
  this.$autocompleteContainer = document.createElement('div')
  // this.$autocompleteContainer.id = 'my-autocomplete-container'

  // create form-group
  const $formGroup = document.createElement('div')
  $formGroup.classList.add('govuk-form-group')

  $formGroup.appendChild($label)
  $formGroup.appendChild(this.$autocompleteContainer)

  return $formGroup
}

SelectOrNew.prototype.getSelectedOption = function (label) {
  console.log('label', label)
  return this.selectOptions.filter(opt => opt[0] === label)
}

SelectOrNew.prototype.getSelectOptions = function () {
  const $options = this.$select.querySelectorAll('option')
  this.selectOptions = Array.from($options).map(($option) => [$option.textContent, $option.value])
  this.selectOptionList = this.selectOptions.map(($option) => $option[0])
  //return Array.from($options).map(($option) => $option.textContent)
}

SelectOrNew.prototype.hideActionPanel = function () {
  this.$actionPanel.classList.remove('new-tag__mode--request')
  this.$actionPanel.classList.remove('new-tag__mode--result')
}

SelectOrNew.prototype.initAccessibleAutocomplete = function () {
  const boundAutoCompleteOnConfirm = this.autoCompleteOnConfirm.bind(this)
  console.log('setup', this.selectOptionList)
  accessibleAutocomplete({
    element: this.$autocompleteContainer,
    id: this.typeAheadId, // To match it to the existing <label>.
    source: this.selectOptionList,
    showNoOptionsFound: false,
    defaultValue: this.lastInputValue,
    onConfirm: boundAutoCompleteOnConfirm
  })

  // store reference to input
  this.$typeAheadInput = this.$typeAheadContainer.querySelector('.autocomplete__wrapper input')
  const boundOnReenterInput = this.onReenterInput.bind(this)
  this.$typeAheadInput.addEventListener('focus', boundOnReenterInput)
}

SelectOrNew.prototype.onConfirmRequest = function (e) {
  e.preventDefault()
  console.log('ajax request to create new event', e)
  console.log(this.$actionPanel.classList)

  this.postNewTag()
}

SelectOrNew.prototype.onReenterInput = function (e) {
  //this.newRecordName = ''
  this.hideActionPanel()
}

SelectOrNew.prototype.postNewTag = function () {
  const tag = {
    name: this.lastInputValue,
  }
  const boundPostNewTagSuccess = this.postNewTagSuccess.bind(this)
  if (this.options.new_backend_endpoint) {
    utils.postToBackend(
      this.options.new_backend_endpoint, tag, boundPostNewTagSuccess
    )
  } else {
    console.log('no new backend endpoint')
  }
}

SelectOrNew.prototype.postNewTagSuccess = function (data) {
  this.showResultPanel()
  const newTag = data.tag
  this.updateSelect(newTag.name, newTag.id)
}

SelectOrNew.prototype.selectOption = function (val) {
  this.$select.value = val
}

SelectOrNew.prototype.setUpActionPanel = function () {
  const $actionPanelFrag = this.$actionPanelTemplate.content.cloneNode(true)
  this.$selectContainer.appendChild($actionPanelFrag)
  return this.$selectContainer.querySelector('.app-action-panel')
}

SelectOrNew.prototype.setUpTypeAhead = function () {
  const labelText = this.$label.textContent
  this.$typeAheadContainer = this.createTypeAheadContainer(labelText)
  this.$selectContainer.insertBefore(this.$typeAheadContainer, this.$actionPanel)

  this.initAccessibleAutocomplete()

  // Handle enter key for input, confirmation panel, and form submission
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault()

      // If confirmation panel is showing, handle "Yes, add it" action
      if (this.$actionPanel.classList.contains('new-tag__mode--request')) {
        this.onConfirmRequest(e)
        return
      }

      // If result panel is showing, submit the form
      if (this.$actionPanel.classList.contains('new-tag__mode--result')) {
        this.$form.submit()
        return
      }

      // Otherwise handle the input value
      const inputValue = this.$typeAheadInput.value.trim()
      if (inputValue === '') {
        return
      }

      if (!this.selectOptionList.includes(inputValue)) {
        // Show the confirmation panel for new tags
        this.lastInputValue = inputValue
        this.showRequestAction(inputValue)
      }
    }
  })
}

SelectOrNew.prototype.showRequestAction = function (val) {
  const $nameEls = this.$actionPanel.querySelectorAll('[data-new-tag="name"]')
  $nameEls.forEach(function ($el) { $el.textContent = val })

  const $confirmBtn = this.$actionPanel.querySelector('[data-new-tag="request"] button')
  const boundOnConfirmRequest = this.onConfirmRequest.bind(this)
  $confirmBtn.addEventListener('click', boundOnConfirmRequest)

  this.$actionPanel.classList.remove('new-tag__mode--result')
  this.$actionPanel.classList.add('new-tag__mode--request')
}

SelectOrNew.prototype.showResultPanel = function () {
  this.$actionPanel.classList.remove('new-tag__mode--request')
  this.$actionPanel.classList.add('new-tag__mode--result')
}

SelectOrNew.prototype.updateSelect = function (name, val) {
  console.log('updating select')
  // check element hasn't already been added
  if (!this.$select.querySelector(`[value="${val}"]`)) {
    this.$select.append(this.createOptionElement(name, val))
    this.selectOption(val)
    this.getSelectOptions()
    this.updateSources()
  }
}

SelectOrNew.prototype.createOptionElement = function (name, val) {
  // Create a new option element
  const $option = document.createElement('option')
  $option.value = val
  $option.textContent = name
  return $option
}

SelectOrNew.prototype.updateSources = function () {
  // replace typeahead
  this.$typeAheadContainer.remove()
  this.setUpTypeAhead()
}

export default SelectOrNew

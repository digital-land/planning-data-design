/* global accessibleAutocomplete */

import utils from '../utils'

function MultiSelect ($module) {
  this.$module = $module
}

MultiSelect.prototype.init = function (params) {
  this.setupOptions(params)
  // get the original form field that needs to be kept updated
  this.$formGroup = this.$module.querySelector('[data-multi-select="form-group"]')
  this.$input = this.$formGroup.querySelector('input')

  // get the options from a hidden select element
  this.$hiddenSelect = this.$module.querySelector('[data-multi-select="select"]')
  this.selectOptions = utils.getSelectOptions(this.$hiddenSelect)
  this.selectOptionLabels = this.selectOptions.map(($option) => $option[0])

  // get the initial set of selections from existing input
  this.currentlySelected = []
  this.initiallySelected()

  // set up a type ahead component
  this.setUpTypeAhead()
  // setup area to display selected
  this.setupSelectedPanel()

  // hide the original form element
  this.$formGroup.classList.add(this.options.hiddenClass)

  return this
}

MultiSelect.prototype.autoCompleteOnConfirm = function (inputValue) {
  console.log(inputValue)
  if (inputValue) {
    const option = this.findOption(inputValue, 'name')
    // if matching option
    if (option.length) {
      // check it isn't already selected
      if (!this.currentlySelected.includes(option[0][1])) {
        this.currentlySelected.push(option[0][1])
        // show in selected panel
        this.displaySelectedItem(option[0])
      }
      // update the original input
      this.updateInput()
    }
    // once processed, empty input if option set
    if (this.options.emptyInputOnConfirm) {
      const $typeAheadInput = this.$typeAheadContainer.querySelector('.autocomplete__input')
      // hacky because autocomplete component calls setState after executing callback
      // so need to wait
      setTimeout(function () {
        $typeAheadInput.value = ''
      }, 150)
    }
    console.log(option)
  }
}

MultiSelect.prototype.createSelectedItem = function (optionPair) {
  const $item = document.createElement('li')
  const $content = document.createElement('div')
  const $label = document.createElement('span')
  $label.classList.add('multi-select__item-label')
  $label.textContent = optionPair[0]
  const $val = document.createElement('span')
  $val.classList.add('multi-select__item-value')
  $val.textContent = optionPair[1]

  const $cancelBtn = document.createElement('a')
  $cancelBtn.classList.add('govuk-link')
  $cancelBtn.classList.add('app-destructive-link')
  $cancelBtn.textContent = 'remove'
  $cancelBtn.href = '#'
  const boundOnDeselectItem = this.onDeselectItem.bind(this)
  $cancelBtn.addEventListener('click', boundOnDeselectItem)

  $content.appendChild($label)
  $content.appendChild($val)

  $item.appendChild($content)
  $item.appendChild($cancelBtn)
  return $item
}

MultiSelect.prototype.onDeselectItem = function (e) {
  e.preventDefault()
  const $deselectBtn = e.currentTarget
  const $item = $deselectBtn.closest('li')
  const val = $item.querySelector('.multi-select__item-value').textContent
  $item.remove()
  console.log('deselect from input', val)
  this.currentlySelected = this.currentlySelected.filter(item => item !== val)
  this.updateInput()
  this.updatePanelContent()
}

MultiSelect.prototype.createSelectedPanel = function () {
  const $panel = document.createElement('div')
  $panel.classList.add('multi-select__select-panel')

  const $heading = document.createElement('h4')
  $heading.classList.add('govuk-heading-s')
  $heading.textContent = `Selected ${this.options.nameOfThingSelecting}`
  const $selectedList = document.createElement('ul')

  const $noSelectionText = document.createElement('p')
  $noSelectionText.classList.add('govuk-hint')
  $noSelectionText.textContent = 'No selections made'

  $panel.append($heading)
  $panel.append($selectedList)
  $panel.append($noSelectionText)
  return $panel
}

MultiSelect.prototype.displaySelected = function () {
  if (this.currentlySelected.length) {
    this.currentlySelected.forEach(function (selection) {
      const option = this.findOption(selection, 'value')
      this.displaySelectedItem(option[0])
    }.bind(this))
  }
  this.updatePanelContent()
}

MultiSelect.prototype.displaySelectedItem = function (option) {
  console.log(option)
  const $list = this.$selectedPanel.querySelector('ul')
  $list.append(this.createSelectedItem(option))
  this.updatePanelContent()
}

MultiSelect.prototype.findOption = function (query, _type) {
  const tupleIndx = (_type === 'value') ? 1 : 0
  return this.selectOptions.filter(opt => opt[tupleIndx] === query)
}

MultiSelect.prototype.getSelectionsFromString = function (str) {
  const selections = str.split(this.options.separator)
  return selections.filter(s => s !== '')
}

MultiSelect.prototype.initAccessibleAutocomplete = function ($container) {
  const boundAutoCompleteOnConfirm = this.autoCompleteOnConfirm.bind(this)
  console.log('setup', this.selectOptionList)
  accessibleAutocomplete({
    element: $container.querySelector('.autocomplete-container'),
    id: $container.querySelector('label').htmlFor, // To match it to the existing <label>.
    source: this.selectOptionLabels,
    showNoOptionsFound: false,
    onConfirm: boundAutoCompleteOnConfirm
  })
}

MultiSelect.prototype.initiallySelected = function () {
  debugger
  const inputString = this.$input.value
  this.currentlySelected = this.getSelectionsFromString(inputString)
}

MultiSelect.prototype.setupSelectedPanel = function () {
  this.$selectedPanel = this.createSelectedPanel()
  this.$module.append(this.$selectedPanel)
  this.displaySelected()
}

MultiSelect.prototype.setUpTypeAhead = function () {
  const labelText = this.$formGroup.querySelector('label').textContent
  this.$typeAheadContainer = utils.createTypeAheadContainer(labelText, this.$hiddenSelect.id)
  this.$module.append(this.$typeAheadContainer)

  this.initAccessibleAutocomplete(this.$typeAheadContainer)
}

// this keeps the hidden input updated
MultiSelect.prototype.updateInput = function () {
  this.$input.value = this.currentlySelected.join(this.options.separator)
}

MultiSelect.prototype.updatePanelContent = function () {
  console.log('update panel content')
  // if no items selected then show no selection msg
  if (this.currentlySelected.length > 0) {
    this.$selectedPanel.classList.remove('multi-select__select-panel--none')
    this.$selectedPanel.classList.add('multi-select__select-panel--selection')
  } else {
    this.$selectedPanel.classList.add('multi-select__select-panel--none')
    this.$selectedPanel.classList.remove('multi-select__select-panel--selection')
  }
}

MultiSelect.prototype.setupOptions = function (params) {
  params = params || {}
  this.options = {}
  this.options.separator = params.separator || ';'
  this.options.nameOfThingSelecting = params.nameOfThingSelecting || 'organistions'
  this.options.hiddenClass = params.hiddenClass || 'app-hidden'
  this.options.emptyInputOnConfirm = params.emptyInputOnConfirm || true
}

export default MultiSelect

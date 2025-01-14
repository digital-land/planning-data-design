/* global accessibleAutocomplete */

import utils from '../utils'

function MultiSelectOrNew($module) {
  this.$module = $module
  this.selectedTags = []
}

MultiSelectOrNew.prototype.init = function(params) {
  this.setupOptions(params)

  // Get elements
  this.$select = this.$module.querySelector('select')
  this.$selectedTagsContainer = this.$module.querySelector('.app-selected-tags')
  this.$selectedTagsInput = this.$module.querySelector('#selected-tags-input')
  this.$form = this.$module.closest('form')

  // Get initial options
  this.selectOptions = Array.from(this.$select.querySelectorAll('option')).map(($option) => ({
    text: $option.textContent,
    value: $option.value
  }))

  // Hide the original select
  this.$select.style.display = 'none'

  // Set up typeahead
  this.setupTypeahead()

  // Set up action panel for new tags
  this.$actionPanelTemplate = document.getElementById(this.options.actionPanelTemplateId)
  this.$actionPanel = this.setupActionPanel()

  // Initialize with any existing tags
  if (this.$selectedTagsInput.value) {
    const tagIds = this.$selectedTagsInput.value.split(',')
    tagIds.forEach(id => {
      const option = this.selectOptions.find(opt => opt.value === id)
      if (option) {
        this.addTag(option)
      }
    })
  }

  // Prevent form submission when confirmation panel is shown
  if (this.$form) {
    this.$form.addEventListener('submit', (e) => {
      if (this.$actionPanel.classList.contains('new-tag__mode--request')) {
        e.preventDefault()
      }
    })
  }

  return this
}

MultiSelectOrNew.prototype.setupOptions = function(params) {
  params = params || {}
  this.options = {
    actionPanelTemplateId: params.actionPanelTemplateId || 'action-panel-template',
    newTagEndpoint: params.newTagEndpoint || false
  }
}

MultiSelectOrNew.prototype.setupTypeahead = function() {
  // Create typeahead container
  const $container = document.createElement('div')
  $container.classList.add('govuk-form-group')

  const $autocomplete = document.createElement('div')
  $container.appendChild($autocomplete)

  // Find the form group that contains the select
  const $formGroup = this.$module.querySelector('#new-tag-form-group')

  // Insert after the existing label
  const $existingLabel = $formGroup.querySelector('label')
  $formGroup.insertBefore($container, $existingLabel.nextSibling)

  // Initialize accessible autocomplete
  accessibleAutocomplete({
    element: $autocomplete,
    id: 'tag-typeahead',
    source: this.selectOptions.map(opt => opt.text),
    showNoOptionsFound: false,
    onConfirm: (inputValue) => this.handleTypeaheadConfirm(inputValue)
  })

  this.$typeaheadInput = $autocomplete.querySelector('input')
}

MultiSelectOrNew.prototype.handleTypeaheadConfirm = function(inputValue) {
  if (!inputValue) return

  const matchingOption = this.selectOptions.find(opt => opt.text === inputValue)

  if (matchingOption) {
    this.addTag(matchingOption)
  } else {
    this.showNewTagConfirmation(inputValue)
  }

  // Clear the input
  setTimeout(() => {
    this.$typeaheadInput.value = ''
  }, 150)
}

MultiSelectOrNew.prototype.addTag = function(tag) {
  if (!this.selectedTags.some(t => t.value === tag.value)) {
    this.selectedTags.push(tag)
    this.renderTags()
    this.updateHiddenInput()
  }
}

MultiSelectOrNew.prototype.removeTag = function(tagValue) {
  this.selectedTags = this.selectedTags.filter(tag => tag.value !== tagValue)
  this.renderTags()
  this.updateHiddenInput()
}

MultiSelectOrNew.prototype.renderTags = function() {
  const html = this.selectedTags.map(tag => `
    <span class="govuk-tag govuk-!-margin-right-1 govuk-!-margin-bottom-1">
      ${tag.text}
      <button type="button" class="app-tag-remove" data-value="${tag.value}" aria-label="Remove ${tag.text}">×</button>
    </span>
  `).join('')

  this.$selectedTagsContainer.innerHTML = html

  // Add click handlers for remove buttons
  this.$selectedTagsContainer.querySelectorAll('.app-tag-remove').forEach(btn => {
    btn.onclick = () => this.removeTag(btn.dataset.value)
  })
}

MultiSelectOrNew.prototype.updateHiddenInput = function() {
  this.$selectedTagsInput.value = this.selectedTags.map(tag => tag.value).join(',')
}

MultiSelectOrNew.prototype.setupActionPanel = function() {
  const $panel = this.$actionPanelTemplate.content.cloneNode(true)
  this.$module.appendChild($panel)
  const $actionPanel = this.$module.querySelector('.app-action-panel')

  // Add click handler for confirm button
  const $confirmBtn = $actionPanel.querySelector('[data-new-tag="request"] button')
  $confirmBtn.addEventListener('click', (e) => this.handleNewTagConfirm(e))

  return $actionPanel
}

MultiSelectOrNew.prototype.showNewTagConfirmation = function(tagName) {
  const $nameEls = this.$actionPanel.querySelectorAll('[data-new-tag="name"]')
  $nameEls.forEach($el => { $el.textContent = tagName })

  this.$actionPanel.classList.remove('new-tag__mode--result')
  this.$actionPanel.classList.add('new-tag__mode--request')

  this.pendingTagName = tagName
}

MultiSelectOrNew.prototype.handleNewTagConfirm = function(e) {
  e.preventDefault()

  if (this.options.newTagEndpoint) {
    utils.postToBackend(
      this.options.newTagEndpoint,
      { name: this.pendingTagName },
      (data) => this.handleNewTagSuccess(data)
    )
  } else {
    console.warn('No new tag endpoint configured')
  }
}

MultiSelectOrNew.prototype.handleNewTagSuccess = function(data) {
  this.$actionPanel.classList.remove('new-tag__mode--request')
  this.$actionPanel.classList.add('new-tag__mode--result')

  const newTag = {
    text: data.tag.name,
    value: data.tag.id
  }

  // Add to options
  this.selectOptions.push(newTag)

  // Add new option to select
  const $option = document.createElement('option')
  $option.value = newTag.value
  $option.textContent = newTag.text
  this.$select.appendChild($option)

  // Add tag to selection
  this.addTag(newTag)
}

export default MultiSelectOrNew

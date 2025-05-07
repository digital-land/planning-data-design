const utils = {}

utils.createTypeAheadContainer = function (labelText, id) {
  // create a label element
  const $label = document.createElement('label')
  $label.classList.add('govuk-label')
  $label.htmlFor = id + '-typeAhead'
  $label.textContent = labelText

  // create the autocomplete container
  const $autocompleteContainer = document.createElement('div')
  $autocompleteContainer.classList.add('autocomplete-container')
  // this.$autocompleteContainer.id = 'my-autocomplete-container'

  // create form-group
  const $formGroup = document.createElement('div')
  $formGroup.classList.add('govuk-form-group')

  $formGroup.appendChild($label)
  $formGroup.appendChild($autocompleteContainer)

  return $formGroup
}

utils.getSelectOptions = function ($select) {
  const $options = $select.querySelectorAll('option')
  return Array.from($options).map(($option) => [$option.textContent, $option.value])
}

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
        onSuccess(data)
      } else {
        console.log('Success:', data)
      }
    })
    .catch((error) => {
      if (onError) {
        onError(error)
      } else {
        console.error('Error:', error)
      }
    })
}


export default utils

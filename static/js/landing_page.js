function languageSwitch(languageCode) {
  const form = document.getElementById('languageForm');
  form.elements.language.value = languageCode;
  form.submit();
}
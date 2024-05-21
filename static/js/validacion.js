function validarCampoVacio(valor) {
  return valor.trim() === "";
}

document
  .getElementById("formulario")
  .addEventListener("submit", function (event) {
    var inputValorUser = document.getElementById("user").value;
    var inputValorPass = document.getElementById("password").value;
    var inputValorPassVeri = document.getElementById("passwordVeri").value;

    if (
      validarCampoVacio(inputValorUser) ||
      validarCampoVacio(inputValorPass)
    ) {
      alert("Hay datos vacios");

      event.preventDefault();
    }
    if (inputValorPass != inputValorPassVeri) {
      alert("Las contraseñas no coinciden");
      event.preventDefault();
    }
  });

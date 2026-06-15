// Função para validar o Registo
function validarRegisto() {

    const username = document.getElementById("usernameID").value.trim();
    const email = document.getElementById("emailID").value.trim();
    const password = document.getElementById("passwordID").value;
    const confirmPassword = document.getElementById("confirmpasswordID").value;

    const usernameRegex = /^[\w]{3,20}$/;
    const passwordRegex = /^[\w]{3,7}$/;

    // Campos obrigatórios
    if (!username || !email || !password || !confirmPassword) {
        alert("Todos os campos são obrigatórios.");
        return false;
    }

    // Username inválido
    if (!usernameRegex.test(username)) {
        alert("Username inválido (3–20 caracteres).");
        return false;
    }

    // Password inválida
    if (!passwordRegex.test(password)) {
        alert("Password inválida (3–7 caracteres).");
        return false;
    }

    // Passwords diferentes
    if (password !== confirmPassword) {
        alert("As palavras-chave não coincidem.");
        return false;
    }

    return true;
}

// Função para validar o Login
function validarLogin() {
    const user = document.getElementById("vatID").value.trim();
    const pass = document.getElementById("passwordID").value;

    if (!user || !pass) {
        alert("Preencha todos os campos.");
        return false;
    }
    return true;
}

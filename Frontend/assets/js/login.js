// 🔐 Connexion utilisateur
async function login(event) {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
        const response = await fetch(API_URL + "/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        // ✅ Le backend retourne "token" (pas "access_token")
        if (data.token) {
            setToken(data.token);
            window.location.href = "dashboard.html";
        } else {
            alert("Login échoué ❌ : " + (data.message || "Identifiants incorrects"));
        }
    } catch (error) {
        alert("Erreur de connexion au serveur ❌");
        console.error(error);
    }
}
document.addEventListener("DOMContentLoaded", () => {
    const addBtn = document.getElementById("add-equipment-btn");
    
    if (addBtn) {
      addBtn.addEventListener("click", () => {
        fetch("/equipment/add/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          body: JSON.stringify({
            name: "Bola Futsal",
            price: 20000,
          }),
        })
        .then(res => res.json())
        .then(data => {
          console.log("Sukses nambah alat:", data);
        });
      });
    }
  });
  
  // Fungsi ambil CSRF token (penting di Django)
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  
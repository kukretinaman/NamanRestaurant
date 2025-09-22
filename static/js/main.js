document.addEventListener("DOMContentLoaded", function() {
    fetch("http://localhost:8000/api/restaurants/")
        .then(res => res.json())
        .then(data => {
            const list = document.getElementById("restaurant-list");
            data.forEach(rest => {
                const li = document.createElement("li");
                li.innerHTML = `<b>${rest.name}</b> - ${rest.cuisine} <br> ${rest.address}`;
                list.appendChild(li);
            });
        });
});

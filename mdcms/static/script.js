const dates = document.getElementsByClassName('date')

// Convert epoch dates to date time strings
for (const d of dates) {
    const opt = { dateStyle: "medium" };
    dt = parseInt(d.innerHTML);
    dt = new Date(dt*1000);
    d.innerHTML = dt.toLocaleString('fr-FR', opt );
}
const dates = document.getElementsByClassName('date');
const header = document.getElementById('header');

// Convert epoch dates to date time strings
for (const d of dates) {
    const opt = { dateStyle: "medium" };
    dt = parseInt(d.innerHTML);
    dt = new Date(dt*1000);
    d.innerHTML = dt.toLocaleString('fr-FR', opt );
}


window.addEventListener("scroll", (event) => {
    let scpos = this.scrollY;
    if (scpos > 100) {
        header.style.fontSize = '.9em';
    } else {
        header.style.fontSize = null;
    }
});
const searchField = document.querySelector("#searchField");
const tableOutput = document.querySelector(".table-output");
const appTable = document.querySelector(".app-table");
const paginationContainer = document.querySelector(".pagination-container");
const noResults = document.querySelector(".no-results");
const tbody = document.querySelector(".table-body");

tableOutput.style.display = "none";

// Debounce function
const debounce = (func, delay) => {
  let timeout;
  return function () {
    const context = this;
    const args = arguments;
    clearTimeout(timeout);
    timeout = setTimeout(() => {
      func.apply(context, args);
    }, delay);
  };
};

const handleSearch = () => {
  const searchValue = searchField.value.trim();

  if (searchValue.length > 0) {
    paginationContainer.style.display = "none";
    tbody.textContent = "";

    fetch("/userincome/search-income/", {
      body: JSON.stringify({ searchText: searchValue }),
      method: "POST",
    })
      .then((res) => res.json())
      .then((data) => {
        console.log("data", data);
        appTable.style.display = "none";
        tableOutput.style.display = "block";

        if (data.length === 0) {
          noResults.style.display = "block";
          tableOutput.style.display = "none";
        } else {
          noResults.style.display = "none";
          data.forEach((item) => {
            const row = document.createElement("tr");
            row.innerHTML = `
              <td>${item.amount}</td>
              <td>${item.source__name}</td>
              <td>${item.description}</td>
              <td>${item.date}</td>`;
            tbody.appendChild(row);
          });
        }
      });
  } else {
    tableOutput.style.display = "none";
    appTable.style.display = "block";
    paginationContainer.style.display = "block";
  }
};

// Add debounce to the input event listener
searchField.addEventListener("keyup", debounce(handleSearch, 300));

document.addEventListener("DOMContentLoaded", function () {
  const botaoAdmin = document.getElementById("btn-adm");
  const botaoCliente = document.getElementById("btn-cli");

  const loginForm = document.querySelector('.cadastro-form');
  if (loginForm) {
    loginForm.addEventListener('submit', function(e) {
      e.preventDefault();
      const isAdmin = window.location.pathname.includes('admin');
      window.location.href = isAdmin ? '/admin/dashboard.html' : '/cliente/cliente - dashboard.html';
    });
  }

  // Menu lateral
  const menuItems = document.querySelectorAll(".menu-item");
  const sections = document.querySelectorAll(".section");

  menuItems.forEach(item => {
    item.addEventListener("click", function(e) {
      e.preventDefault();
      const targetSection = this.getAttribute("data-section");

      sections.forEach(section => {
        section.style.display = "none";
      });

      document.getElementById(targetSection).style.display = "block";

      menuItems.forEach(menuItem => {
        menuItem.classList.remove("active");
      });

      this.classList.add("active");
    });
  });

  const documentList = document.getElementById('document-list');
  if (documentList) {
    fetch('/api/documentos')
        .then(response => response.json())
        .then(data => {
            if (data.documentos && data.documentos.length > 0) {
                documentList.innerHTML = data.documentos.map(doc => `
                    <div class="file-item">
                        <span class="file-name">${doc.nome}</span>
                        <div class="file-actions">
                            <a href="/download/${doc.arquivo}" class="action-btn">Baixar</a>
                            <a href="/view/${doc.arquivo}" class="action-btn" target="_blank">Visualizar</a>
                        </div>
                    </div>
                `).join('');
            } else {
                documentList.innerHTML = '<p>Nenhum documento encontrado.</p>';
            }
        });
  }
});
        // Objeto para armazenar os arquivos por cliente
        let clientFiles = {};

        // Funções para o modal de arquivos
        let currentClient;

        function openFileModal(link, clientName, files) {
            currentClient = clientName;
            const modal = document.getElementById('file-modal');
            const fileList = document.getElementById('file-list');
            const clientNameSpan = document.getElementById('file-client-name');

            clientNameSpan.textContent = clientName;
            fileList.innerHTML = '';

            if (files && files.length > 0) {
                files.forEach(fileName => {
                    const fileItem = document.createElement('div');
                    fileItem.className = 'file-item';
                    fileItem.innerHTML = `
                        <span class="file-name">${fileName}</span>
                        <div class="file-actions">
                            <button onclick="viewFile('${fileName}')" class="action-btn">
                                <i class="fas fa-eye"></i> Visualizar
                            </button>
                            <button onclick="downloadFile('${fileName}')" class="action-btn">
                                <i class="fas fa-download"></i> Baixar
                            </button>
                            <button onclick="printFile('${fileName}')" class="action-btn">
                                <i class="fas fa-print"></i> Imprimir
                            </button>
                            <button onclick="deleteFile('${fileName}')" class="action-btn delete">
                                <i class="fas fa-trash"></i> Excluir
                            </button>
                        </div>
                    `;
                    fileList.appendChild(fileItem);
                });
            } else {
                fileList.innerHTML = '<p class="no-files">Nenhum arquivo adicionado.</p>';
            }

            modal.style.display = 'block';
        }

        function viewFile(fileName) {
            const clientData = JSON.parse(localStorage.getItem('clientsData')) || [];
            const client = clientData.find(c => c.nome === currentClient);
            if (client && client.files) {
                const fileURL = URL.createObjectURL(new Blob([client.files[fileName]]));
                window.open(fileURL, '_blank');
            }
        }

        function downloadFile(fileName) {
            const clientData = JSON.parse(localStorage.getItem('clientsData')) || [];
            const client = clientData.find(c => c.nome === currentClient);
            if (client && client.files) {
                const link = document.createElement('a');
                link.href = URL.createObjectURL(new Blob([client.files[fileName]]));
                link.download = fileName;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }
        }

        function printFile(fileName) {
            const clientData = JSON.parse(localStorage.getItem('clientsData')) || [];
            const client = clientData.find(c => c.nome === currentClient);
            if (client && client.files) {
                const fileURL = URL.createObjectURL(new Blob([client.files[fileName]]));
                const iframe = document.createElement('iframe');
                iframe.style.display = 'none';
                iframe.src = fileURL;
                document.body.appendChild(iframe);
                iframe.contentWindow.print();
            }
        }

        function deleteFile(fileName) {
            if (confirm('Tem certeza que deseja excluir este arquivo?')) {
                const clientData = JSON.parse(localStorage.getItem('clientsData')) || [];
                const clientIndex = clientData.findIndex(c => c.nome === currentClient);
                if (clientIndex !== -1) {
                    const files = clientData[clientIndex].files || [];
                    const fileIndex = files.indexOf(fileName);
                    if (fileIndex !== -1) {
                        files.splice(fileIndex, 1);
                        clientData[clientIndex].files = files;
                        localStorage.setItem('clientsData', JSON.stringify(clientData));
                        openFileModal(null, currentClient, files);
                    }
                }
            }
        }

// Recarregar processos quando mudar para a aba de processos
document.querySelectorAll('.menu-item').forEach(item => {
    item.addEventListener('click', function (e) {
        const section = this.getAttribute('data-section');
        switch (section) {
            case 'pedidos':
            carregarProcessosCliente();
                break;
                case 'meus-clientes':
                    carregarClientes();
                    break;
                case 'andamentos':
                    carregarAndamentos();
                    break;
        }


    });
});

// Function to load client profile data

async function carregarPerfilCliente() {
    try {
        const cpf = localStorage.getItem('clienteCPF'); // CPF armazenado no localStorage
        const response = await fetch(`/api/clientes/${cpf}`);
        const cliente = await response.json();

        if (cliente.success) {
            document.getElementById('nome').value = cliente.data.nome;
            document.getElementById('telefone').value = cliente.data.telefone;
            document.getElementById('email').value = cliente.data.email;
            document.getElementById('cpf').value = cliente.data.cpf;
            document.getElementById('rg').value = cliente.data.rg;
            document.getElementById('cnh').value = cliente.data.cnh;
            document.getElementById('renavam').value = cliente.data.renavam;
            document.getElementById('placa').value = cliente.data.placa;
            document.getElementById('endereco').value = cliente.data.endereco;
        } else {
            alert('Erro ao carregar os dados do cliente.');
        }
    } catch (error) {
        console.error('Erro ao carregar perfil do cliente:', error);
    }
}

// Function to upload client files
async function enviarArquivosCliente() {
    try {
        const cpf = localStorage.getItem('clienteCPF');
        const arquivos = document.getElementById('documentos').files;
        const formData = new FormData();

        for (const arquivo of arquivos) {
            formData.append('arquivos', arquivo);
        }

        const response = await fetch(`/api/clientes/${cpf}/arquivos`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        if (result.success) {
            alert('Arquivos enviados com sucesso!');
        } else {
            alert('Erro ao enviar os arquivos.');
        }
    } catch (error) {
        console.error('Erro ao enviar arquivos do cliente:', error);
    }
}


// Admin Login
const loginForm = document.querySelector('.login-form');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const email = document.getElementById('email').value;
        const senha = document.getElementById('senha').value;
        const formData = {
            email,
            senha
        };

        try {
            const response = await fetch('/api/admin/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (response.ok) {
                window.location.href = '/admin/dashboard.html';
            } else {
                alert('Erro ao fazer login. Verifique suas credenciais e tente novamente.');
            }
        } catch (error) {
            console.error('Erro durante o login:', error);
            alert('Erro ao tentar fazer login. Verifique sua conexão e tente novamente.');
        }
          });
        }
        }
    // Side menu
    const menuItems = document.querySelectorAll(".nav-link");
    menuItems.forEach(item => {
    item.addEventListener("click", function(e) {
        e.preventDefault();
        const href = this.getAttribute("href");
        window.location.href = href;
    });
    });

// Adding events to buttons

window.addEventListener('load', carregarPerfilCliente);
window.addEventListener('load', carregarProcessosCliente);
document.getElementById('salvar-perfil')?.addEventListener('click', carregarPerfilCliente);
document.getElementById('enviar-arquivos')?.addEventListener('click', enviarArquivosCliente);


// Function to load client processes
async function carregarProcessosCliente() {
    try {
        const cpf = localStorage.getItem('clienteCPF') || '123.456.789-00'; // Use o CPF armazenado ou um padrão
        const response = await fetch(`/api/meus-processos/${cpf}`);
        const data = await response.json();

        const tbody = document.querySelector('#pedidos-table tbody');
        tbody.innerHTML = '';

        if (data.processos && data.processos.length > 0) {
            data.processos.forEach(processo => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${processo.nome_cliente}</td>
                    <td>${processo.processo_numero}</td>
                    <td>${processo.prazo}</td>
                    <td>${processo.sobre}</td>
                    <td>${processo.status}</td>
                `;
                tbody.appendChild(tr);
            });
        } else {
            document.getElementById('no-processes-message').style.display = 'block';
        }
    } catch (error) {
        console.error('Erro ao carregar processos:', error);
    }
}



    async function carregarAndamentos() {
        try {
            const response = await fetch('/api/andamentos');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const andamentosData = await response.json();
            updateAndamentosTable(andamentosData);
        } catch (error) {
            console.error('Erro ao carregar andamentos:', error);
            alert('Erro ao carregar andamentos. Verifique o console para detalhes.');
        }
    }

    window.addEventListener('load', carregarAndamentos);


    async function carregarClientes() {
        // Implementar
    }


    try {
        const cpf = localStorage.getItem('clienteCPF');
        const arquivos = document.getElementById('documentos').files;
        const formData = new FormData();

        for (const arquivo of arquivos) {
            formData.append('arquivos', arquivo);
        }

        const response = await fetch(`/api/clientes/${cpf}/arquivos`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        if (result.success) {
            alert('Arquivos enviados com sucesso!');
        } else {
            alert('Erro ao enviar os arquivos.');
        }
    } catch (error) {
        console.error('Erro ao enviar arquivos do cliente:', error);
    }
}

// Adicionar eventos aos botões
window.addEventListener('load', carregarPerfilCliente);
document.getElementById('salvar-perfil').addEventListener('click', salvarPerfilCliente);
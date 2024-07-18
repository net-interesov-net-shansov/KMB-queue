var socket = io();
let data = [];
let operators = window.appConfig.operator;
let operations = window.appConfig.operations
let currentTask = null;
let currentCabinet = null;
let opr;

// проверка связи
socket.on('connect', function() {
  console.log('Связь есть');
});

console.log(operators);
console.log(operations);



//обнавление таблицы вывода
socket.on('queue_update', function(json) {
  if (data.length == 0) {
    data.push(json.queue);
  } else {
    data = [];
    data.push(json.queue);
  }
  // вывод очереди
  console.log(data);

  const userSelectElement = document.getElementById('user-select');
  userSelectElement.innerHTML = '<option value="">Выберите пользователя</option>';

  

  data[0].forEach(user => {
    //console.log(user)

    if (operators.operations.split('').some(letter => user.operation.includes(letter)) && user.status === 'waiting' || user.status === 'True') {
      const optionElement = document.createElement('option');
      optionElement.value = user.number;
      optionElement.textContent = user.number;
      userSelectElement.appendChild(optionElement);

      const soundFile = new Audio('/static/audio/dutifully-notification-tone.mp3');
      soundFile.autoplay = true;
    };
  });


});


// Для осуществления выбора и вывода информации по выбранному персонажу
const userSelectElement = document.getElementById('user-select');
userSelectElement.addEventListener('change', function() {

  const userId = userSelectElement.value;
  currentTask = userSelectElement.value;
  document.getElementById('current-task').textContent = `Вы выбрали: ${userId}`;

  data[0].forEach(user => {
    if (user.number === parseInt(userId)) {
      operations.forEach(operation => {
        if (operation.operation_code === user.operation) {
          opr = operation.operation_name;
          currentCabinet = operation.cabinet;
        }
      });

      function generateTable(userNumber, opr, userBirthdate, userUsername, userPhone, userLastname) {
        const oldTable = document.getElementById("operator-table");
        if (oldTable) {
          oldTable.parentNode.removeChild(oldTable);
        }
      
        const tableHtml = `
          <table id="operator-table" style="margin-bottom: 2vh; margin-top: 2vh;">
            
              <tr>
                <th>Талон</th>
                <td>${userNumber}</td>
              </tr>
              <tr>
                <th>Имя/Фамилия</th>
                <td>${userUsername} ${userLastname}</td>
              </tr>
              <tr>
                <th>Телефон</th>
                <td>${userPhone}</td>
              </tr>
              <tr>
                <th>Операция</th>
                <td>${opr}</td>
              </tr>
              <tr>
                <th>День рождения</th>
                <td>${userBirthdate}</td>
              </tr>           
          </table>
        `;
        const tableContainer = document.getElementById("table_container")
        tableContainer.innerHTML = tableHtml;
      }
      
      generateTable(user.number, opr, user.birthdate, user.username, user.phone, user.userLastname)
    };
  });
});

var isFinished = false;

$('#assign-cabinet').on('click', function() {
  if (currentTask && currentCabinet) {
    if (!isFinished) {
      socket.emit('assign_cabinet', { number: currentTask, cabinetId: currentCabinet });
      console.log(`Кабинет ${currentCabinet} назначен пользователю ${currentTask}`);
      $(this).text('Закончить приём');
      isFinished = true;
    } else {
      socket.emit('unassign_cabinet', { number: currentTask, cabinetId: currentCabinet });
      console.log(`Кабинет ${currentCabinet} отменен для пользователя ${currentTask}`);
      $(this).text('Назначить кабинет');
      isFinished = false;
    }
  } else {
    alert("Перед назначением выберите задачу и кабинет.");
  }
});


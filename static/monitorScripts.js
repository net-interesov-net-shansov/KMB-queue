let operations = window.appConfig.operations;

var socket = io();

console.log(operations);

socket.on('connect', function() {
    console.log('Связь есть');
    
});

socket.on('queue_update', function(data) {
  console.log(data);
  const queueList = data.queue.filter((item) => item.status === 'waiting').map((item) => `${item.number}`);
  document.getElementById("queue-list").innerHTML = queueList.join(", ");
});
  
let uniqueData = [];
let tableRows = {};

function playSound() {
  const soundFile1 = new Audio('/static/audio/dutifully-notification-tone.mp3');

  if (soundFile1) {
    console.log(soundFile1)
    soundFile1.autoplay = true;
  } else {
    console.log(error)
  }
}

socket.on('queue_update', function(data) {
  console.log(data);

  const table = document.getElementById('queue-table');

  data.queue.forEach((item) => {
    let cabinetText = operations.find((operations) => operations.operation_code === item.operation);

    if (item.status === 'True') {
      if (!uniqueData.find((uniqueItem) => uniqueItem.number === item.number)) {
        uniqueData.push(item);

        playSound();

        const row = table.insertRow(-1);
        row.innerHTML = `
          <td>${item.username}</td>
          <td>${item.number}</td>
          <td>${cabinetText.cabinet}</td>
        `;
        tableRows[item.number] = row;
      }




    } else if (item.status === 'False') {
      if (uniqueData.find((uniqueItem) => uniqueItem.number === item.number)) {
        const index = uniqueData.indexOf(item);
        if (index > -1) {
          uniqueData.splice(index, 1);
        }

        if (tableRows[item.number]) {
          table.deleteRow(tableRows[item.number].rowIndex);
          delete tableRows[item.number];
        }
      }
    }
  });
});



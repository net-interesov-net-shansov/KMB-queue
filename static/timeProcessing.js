$(document).ready(function() {
  $("#time").text(getTime());
})

setInterval(() => {
  $("#time").text(getTime());
}, 10 * Math.pow(10, 3));

function getDayOfTheWeek(i) {
  let arr = {
    1: "ПН",
    2: "ВТ",
    3: "СР", 
    4: "ЧТ",
    5: "ПТ",
    6: "СБ",
    7: "ВС"
  }
  if (i > 0 && i < 8) { 
    return arr[i];
  }
  return 0;
}

// export function getTime() {
//   let current = new Date()
//   let hours = current.getUTCHours();
//   let minutes = current.getUTCMinutes();
//   let day = getDayOfTheWeek(current.getDay());
  
//   hours = (hours < 10? "0" : "") + hours;
//   minutes = (minutes < 10? "0" : "") + minutes;
  
//   let curr_time = `${day}, ${hours}:${minutes}`;
//   return curr_time;
// }

export function getTime() {
  let current = new Date()
  let utcHours = current.getUTCHours();
  let utcMinutes = current.getUTCMinutes();
  let utcSeconds = current.getUTCSeconds();
  
  // Add 3 hours to UTC time
  let utcPlus3Hours = utcHours + 3;
  
  // Handle cases where the hour exceeds 23
  if (utcPlus3Hours > 23) {
    utcPlus3Hours -= 24;
  }
  
  let hours = (utcPlus3Hours < 10? "0" : "") + utcPlus3Hours;
  let minutes = (utcMinutes < 10? "0" : "") + utcMinutes;
  
  let day = getDayOfTheWeek(current.getUTCDay());
  
  let curr_time = `${day}, ${hours}:${minutes}`;
  return curr_time;
}
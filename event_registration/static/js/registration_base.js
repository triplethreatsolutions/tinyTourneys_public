// Fetch context from template
const event_data = JSON.parse(document.getElementById('data').textContent)
const spinner = document.getElementById("spinner");

let currentTab = 0; // Current tab is set to be the first tab (0)
let summaryReached = false;
let registrationData = {};
let stripe_config = 0;
let quantity = 0;

let states = [
    'Alabama',
    'Alaska',
    'Arizona',
    'Arkansas',
    'California',
    'Colorado',
    'Connecticut',
    'Delaware',
    'Dist. of Columbia',
    'Florida',
    'Georgia',
    'Hawaii',
    'Idaho',
    'Illinois',
    'Indiana',
    'Iowa',
    'Kansas',
    'Kentucky',
    'Louisiana',
    'Maine',
    'Maryland',
    'Massachusetts',
    'Michigan',
    'Minnesota',
    'Mississippi',
    'Missouri',
    'Montana',
    'Nebraska',
    'Nevada',
    'New Hampshire',
    'New Jersey',
    'New Mexico',
    'New York',
    'North Carolina',
    'North Dakota',
    'Ohio',
    'Oklahoma',
    'Oregon',
    'Pennsylvania',
    'Puerto Rico',
    'Rhode Island',
    'South Carolina',
    'South Dakota',
    'Tennessee',
    'Texas',
    'Utah',
    'Vermont',
    'Virginia',
    'Washington',
    'West Virginia',
    'Wisconsin',
    'Wyoming'
]

initializeFormData(); // Init form context for event
showTab(currentTab); // Display the current tab

function getCookie(name) {
   let cookieValue = null;
   if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function initializeFormData() {
   let sel = document.getElementById("division-select-id-1");

   // Add available divisions to drop down list
   for (let i=0; i<event_data["divisions"].length; i++) {
       let opt = document.createElement("option");
       opt.value = event_data["divisions"][i];
       opt.text = event_data["divisions"][i];
       sel.add(opt, null);
   }
   initializeEventListeners()
   initializeStateData()

   // Initialize promo code to nothing until we confirm its enabled
   registrationData["promocode"] = "..."

}

function initializeEventListeners(){
   // add event for adding more teams
   document.querySelector('#addBtn').addEventListener('click', function(){
      addTeamForm()
   }, true)

   // add event listener for prev/next button elements
   document.querySelector('#nextBtn').addEventListener('click', function (){
      nextPrev(1)
   }, true)
   document.querySelector('#prevBtn').addEventListener('click', function (){
      nextPrev(-1)
   }, true)
   document.querySelector('#team-tab').addEventListener('click', function (e){
      deleteTeamForm(e.target)
   }, true)
}

function initializeStateData() {
    let sel = document.getElementById("state-select");

    for (let i = 0; i < states.length; i++) {
       let opt = states[i];
       let el = document.createElement("option");
       el.textContent = opt;
       el.value = opt;
       sel.appendChild(el);
   }
}

let formatPhoneNumber = (str) => {
  //Filter only numbers from the input
  let cleaned = ('' + str).replace(/\D/g, '');

  //Check if the input is of correct length
  let match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);

  if (match) {
    return '(' + match[1] + ') ' + match[2] + '-' + match[3]
  }

  return null
};

function teamsRegistered(){

   // Find out how many teams they decided to register
   let teams = document.getElementsByClassName("new-team")
   // Determine how many teams the user is trying to register
   quantity = teams.length

   let re_team = /team-id-/; // literal notation

   // Extract all the keys from the registration data
   let indexes = Object.keys(registrationData)

   // Get the parent element to generate the teams listed
   let teams_div = document.getElementById("team-listing")

   // Double check we don't already have teams listed as registered
   if(teams_div.hasChildNodes()){
      while (teams_div.firstChild) {
        teams_div.removeChild(teams_div.firstChild);
      }
   }

   let unordered_list = document.createElement('ul')
   teams_div.appendChild(unordered_list)

   // Init team array, will hold a list of registered teams for the API
   let team_array = []

   indexes.forEach(function(element) {
      // Find all the team-id- elements
      if(element.match(re_team)){
         let digit = element[element.search(/\d/g)]

         // Create a dict for each registered team and push it to the array
         team_array.push({name: registrationData[element],
                        division_id: event_data[registrationData['division-select-id-' + digit]],
                        division: registrationData['division-select-id-' + digit]})

         // find the team id number associated with this entry
         // create the list item and assign the team name associated with the team id element
         let list_item = document.createElement('li')
         let span_item = document.createElement('span')
         span_item.textContent = " ( " + registrationData['division-select-id-' + digit] + " Division )";
         list_item.textContent = registrationData[element]
         list_item.appendChild(span_item)
         unordered_list.appendChild(list_item)
      }
   })
   // Load array back into the registration data
   registrationData["teams"] = team_array

   return quantity
}

function initializeSummary(){
   let promo = String("...")
   if(registrationData["promocode"]){
      promo = registrationData["promocode"]
   }
   else{
      registrationData["promocode"] = promo
   }

   let event = event_data["eventSlug"]
   let fees = getRegistrationFees(promo, event, teamsRegistered())
}

function loadSummary(data){

   if(event_data["promoEnabled"] === true){
      document.getElementById("promo-code").textContent = registrationData["promocode"];
      document.getElementById("discount").textContent = data["discount"]
   }

   document.getElementById("cost").textContent = data["cost"]
   document.getElementById("fees").textContent = data["fees"]
   document.getElementById("total-cost").textContent = data["total_cost"]

   document.getElementById("registration-heading").textContent = "Registration Summary";
   document.getElementById("name").textContent = registrationData["fname"] + " " +  registrationData["lname"]
      + " (" + registrationData["role"] + ")";
   document.getElementById("email").textContent = registrationData["email"];
   document.getElementById("phone").textContent = registrationData["phone"];
   document.getElementById("address").textContent = registrationData["address"];
   document.getElementById("city").textContent = registrationData["city"] + ', ' + registrationData["state"]
      + " " + registrationData["zip"];
   document.getElementById("comments").textContent = registrationData["comments"];
}

let getRegistrationFees = function (promo, event, quantity) {
   spinner.removeAttribute('hidden');
   return fetch('/registration/registration-fees/', {
         method: 'POST',
         headers: {
            'Content-Type': 'application/json',
            'X-CSRFTOKEN': getCookie('csrftoken'),
         },
         body: JSON.stringify({
            promocode: promo,
            event_slug: event,
            quantity: quantity,
         }),
      }).then(function (result) {
         return result.json();
      }).then(function (data){
         loadSummary(data)
         spinner.setAttribute('hidden', '');
         return data;
   }).catch(error => {
      console.error('There has been a problem with your fetch operation:', error);
  });
};




let addTeamForm = function () {
   let team_count = document.getElementsByName("team")
   let count = team_count.length + 1

   let div = document.getElementById("team-tab");

   // Create a main container
   let team_add_container = document.createElement("div")
   team_add_container.className = "team-add-container"
   div.appendChild(team_add_container)

   // Create a stylish divider between each unique team input section
   let div_sep = document.createElement("div")
   div_sep.className = "team-separator"
   team_add_container.appendChild(div_sep)

   // create container to host team input and remove button
   let input_container = document.createElement("div")
   input_container.className = "team-container"

   // Add Team Name Input
   let input = document.createElement("input")
   input.id = "team-id-" + count.toString()
   input.className = "new-team"
   input.name = "team"
   input.placeholder = "Team #"+ + count.toString() + " Name..."
   input.required = true
   input_container.appendChild(input)

   // Add remove button option
   let span = document.createElement("span")
   span.innerHTML = "<a class=\"btn btn-lg btn-yellow btn-small-text delete\">X" + "</a>"
   input_container.appendChild(span)

   // Add label for Division select drop-down
   let div_label = document.createElement("label")
   div_label.id = "division-label-id-" + count.toString()
   div_label.className = "division-label"
   div_label.htmlFor = "division-select-id-" + count.toString()
   div_label.innerText = "Choose Division:"

   // Create select drop-down options
   let select = document.createElement("select")
   // Add available divisions to drop down list
   select.id = "division-select-id-" + count.toString()
   select.name = "division"
   select.className = "division-select"
   select.required = true
   let opt = document.createElement("option");
   opt.text = "--Please choose a division--";
   opt.value = ""
   select.add(opt)
   for (let i=0; i<event_data["divisions"].length; i++) {
      let opt = document.createElement("option");
      opt.value = event_data["divisions"][i];
      opt.text = event_data["divisions"][i];
      select.add(opt, null);
    }

   // add division select elements to main container
   team_add_container.appendChild(input_container)
   team_add_container.appendChild(div_label)
   team_add_container.appendChild(select)
}

let deleteTeamForm = function (el){
   if(el.classList.contains('delete')){
      // need to find the main container three levels up to remove everything
      el.parentElement.parentElement.parentElement.remove()

      // find out how many team entries are remaining
      let teams = document.getElementsByClassName("new-team")
      let divisions = document.getElementsByClassName("division-select")
      let labels = document.getElementsByClassName("division-label")

      // Update remaining team entry forms
      let count = 1
      for (const team of teams){
         team.placeholder = "Team #" + count.toString() + " Name..."
         team.id = "team-id-" + count.toString()
         count++
      }

      count = 1
      for (const division of divisions){
         division.id = "division-select-id-" + count.toString()
         count++
      }

      count = 1
      for (const label of labels){
         label.id = "division-label-id-" + count.toString()
         label.htmlFor = "division-select-id-" + count.toString()
         count++
      }
   }
   // reset the registration form data
   registrationData= {}
}

let registerCheckoutEvent = function (){
   // Register the 'nextBtn' element for a checkout redirect
   document.querySelector('#nextBtn').addEventListener('click', setupCheckoutSession, true)
}

let unregisterCheckoutEvent = function (){
   // Register the 'nextBtn' element for a checkout redirect
   document.querySelector('#nextBtn').removeEventListener('click', setupCheckoutSession, true);
}

function scrubRegistrationData() {
   // Remove initial team and division data once summary is load and user is ready to checkout
   for(let i = 1; i <= quantity; i++ ){
      delete registrationData['team-id-' + i]
      delete registrationData['division-select-id-' + i]
   }
}

// Create a Checkout Session with the selected quantity
let createCheckoutSession = function () {
   registrationData["event_slug"] = event_data["eventSlug"]
   spinner.removeAttribute('hidden');
  return fetch('/registration/create-checkout-session', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFTOKEN': getCookie('csrftoken'),
    },
    body: JSON.stringify({
        quantity: quantity,
        data: registrationData,
    }),
  }).then(function (result) {
      spinner.setAttribute('hidden', '');
      return result.json();
  });
};

let setupCheckoutSession = function () {
    spinner.removeAttribute('hidden');
    scrubRegistrationData();
    getCheckoutConfigs()

}

function getCheckoutConfigs() {
   spinner.removeAttribute('hidden');
   /* Get your Stripe publishable key to initialize Stripe.js */
    fetch('/registration/config/')
        .then(function (result) {
            return result.json();
        })
        .then(function (json) {
         window.config = json;
         stripe_config = Stripe(config.publicKey, {
            stripeAccount: event_data["connected_account"]});
        
         createCheckoutSession()
             .then(function (data) {
                stripe_config.redirectToCheckout({
                            sessionId: data.sessionId,
                        })
                   .then((handleResult) => {
                        if(handleResult.error)
                        {
                            console.log(handleResult.error.message)
                            alert(handleResult.error.message)
                        }
                        spinner.setAttribute('hidden', '');
                        });
                });
        
        
    })

}

function showTab(n) {
  // This function will display the specified tab of the form...
  let x = document.getElementsByClassName("tab");
  // Grab input elements and clear out the class assignments
  let y = x[n].getElementsByTagName("input");
  for (let i = 0; i < y.length; i++) {
     y[i].className += "";
  }
  x[n].style.display = "block";

  //... and fix the Previous/Next buttons:
  if (n === 0) {
      document.getElementById("prevBtn").style.display = "none";
      document.getElementById("addBtn").style.display =  "inline-block";
  } else {
      document.getElementById("prevBtn").style.display = "inline";
      document.getElementById("addBtn").style.display =  "none"
  }
  if (n === (x.length - 1)) {
     summaryReached = true;
     initializeSummary();
     document.getElementById("nextBtn").innerHTML = "Checkout";
     registerCheckoutEvent();
     // Take focus off checkout button
      document.getElementById("nextBtn").blur();
  } else {
     // if registration summary reached, and user has gone back, unregister the checkout event
     if(summaryReached){
        unregisterCheckoutEvent();
        summaryReached = false;
     }
      document.getElementById("nextBtn").innerHTML = "Next";
      // Set focus on first input element
      document.getElementById(y[0].id).focus();
  }
  //... and run a function that will display the correct step indicator:
  fixStepIndicator(n)

}

let nextPrev = function (n) {
  // This function will figure out which tab to display
  let x = document.getElementsByClassName("tab");
  // Exit the function if any field in the current tab is invalid:
  if (n === 1 && !validateForm()) return false;

   // Hide the current tab:
   x[currentTab].style.display = "none";
   // Increase or decrease the current tab by 1:
   currentTab = currentTab + n;

  // if you have reached the end of the form...
  if (currentTab >= x.length) {
     x[currentTab-1].style.display = "block";
  }else
  {
      showTab(currentTab);
  }

  // Otherwise, display the correct tab:

}

function validateDivisionSelection(tab){
   let valid = true

    if(tab.id === "team-tab")
    {
        // Check for division select drop down element and validate
        let divisions = document.getElementsByName("division")
       for (let i = 0; i < divisions.length; i++) {
          if (typeof divisions[i] != 'undefined' && divisions[i] != null) {
             let strDivision = divisions[i].options[divisions[i].selectedIndex].value;
             if (strDivision === "") {
                divisions[i].className = "division-select invalid";
                valid = false;
             } else {
                divisions[i].className = "division-select";
                registrationData[`${divisions[i].id}`] = strDivision;
             }
          }
       }
    }

   return valid
}

function validateStateSelection() {
   let valid = true
   // Check for state select drop down element and validate
  let e = document.getElementById("state-select");
  if(typeof(e) != 'undefined' && e != null){
     let strState = e.options[e.selectedIndex].value;
     // This currentTab == 2 is a hack until I can handle this Select element better, currently
     // it is a bug from preventing the form from advancing after the first tab.
     if (strState === "" && currentTab === 2){
        e.className = "invalid";
        valid = false;
     }else{
        e.className = "";
        registrationData[`${e.name}`] = strState;
     }
  }

  return valid
}

function validateFullName(entry){
   // Split full name into first and last
    const words = entry.value.split(' ');
    registrationData['fname'] = words[0]
   // If user forgot to enter last name...default to '-'
   if (words[1] == undefined){
      words[1] = "-"
   }
    registrationData['lname'] = words[1]
}

function validateEmail(entry){
   registrationData[entry.name] = entry.value
}

function validateRole(entry){
   // Only store the radio state that is selected
   if(entry.checked === true)
   {
      registrationData["role"] = entry.value
   }
}

function validateAddress(entry){

   if(entry.name === 'address'){
      registrationData[entry.name] = entry.value
   }
   else if(entry.name === 'city'){
      registrationData[entry.name] = entry.value
   }
   else if(entry.name === 'state'){
      registrationData[entry.name] = entry.value
   }
   else if(entry.name === 'zip'){
      registrationData[entry.name] = entry.value
   }
}

function validatePhoneNumber(entry) {
   // Ensure phone given is formatted properly
   registrationData['phone'] = formatPhoneNumber(entry.value)
}

function validateComments(entry){
   if(entry.value === ""){
      registrationData[entry.name] = "..."
   }
   else{
      registrationData[entry.name] = entry.value
   }
}

function validatePromo(entry){
   if(entry.value === ""){
      registrationData[entry.name] = "..."
   }
   else{
      registrationData[entry.name] = entry.value
   }
}


function validateForm() {
   // This function deals with validation of the form fields
   let x, y, i, valid = true;
   // Get current tab
   x = document.getElementsByClassName("tab");
   // Get all of the input elements in the tab
   y = x[currentTab].getElementsByTagName("input");

   if(!validateDivisionSelection(x[currentTab])) {
      alert("Must select a division for each team.")
      return false
   }

   if(!validateStateSelection()) { return false }

  // A loop that checks every input field in the current tab:
  for (i = 0; i < y.length; i++) {
      // If a field is empty...
      if (y[i].value === "" && y[i].name !== "comments" && y[i].name !== "promocode") {
          // add an "invalid" class to the field:
          y[i].className += " invalid";
          // and set the current valid status to false
          valid = false;
          break;
      }
      else if ((y[i].name === 'phone') && (y[i].type === 'tel')){
         validatePhoneNumber(y[i])
      }
      else if (y[i].name === 'email'){
         validateEmail(y[i])
      }
      else if((y[i].name === 'fullname')){
         validateFullName(y[i])
      }
      else if((y[i].name === 'role') && (y[i].type === 'radio')){
         validateRole(y[i])
      }
      else if((y[i].name === 'address') ||
         (y[i].name === 'city') ||
         (y[i].name === 'state') ||
         (y[i].name === 'zip')){
         validateAddress(y[i])
      }
      else if(y[i].name === 'comments'){
         validateComments(y[i])
      }
      else if(y[i].name === 'promocode'){
         validatePromo(y[i])
      }
      else {
         // Catch everything else that didn't have a validation check
         registrationData[`${y[i].id}`] = y[i].value
      }

  }
  // If the valid status is true, mark the step as finished and valid:
  if (valid) {
      document.getElementsByClassName("step")[currentTab].className += " finish";
  }

  return valid; // return the valid status
}

function fixStepIndicator(n) {
  // This function removes the "active" class of all steps...
  let i, x = document.getElementsByClassName("step");
  for (i = 0; i < x.length; i++) {
    x[i].className = x[i].className.replace(" active", "");
  }
  //... and adds the "active" class on the current step:
  x[n].className += " active";
}

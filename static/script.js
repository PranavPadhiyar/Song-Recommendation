$(document).ready(function() {

  const elementToObserve = document.getElementById('selected-songs');
  const getRecommendationsButton = document.getElementById('get-recommendations-button');
  const songSearchButton = document.getElementById('song-name-button');

  const songSearchInput = document.getElementById('song-name-input');

  songSearchInput.addEventListener('keypress', function(e) {
    if(e.key === 'Enter') {
      songSearchButton.click();
    }
  })
  // Create a new observer instance
  const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      // Check if the inner HTML of the element has changed
      if (mutation.type === 'childList' && mutation.target === elementToObserve) {
        const numItems = elementToObserve.childElementCount
        getRecommendationsButton.disabled = !( numItems >= 3 && numItems <= 5);
        
        console.log(numItems);
        if (numItems == 5) {
          document.getElementById('song-search-form').innerHTML = ""
        }

      }
    });
  });


  const mood_slider = document.getElementById("mood-slider");
  const focus = document.getElementById('focus');
  const study = document.getElementById('study');
  const neutral = document.getElementById('neutral');
  const happy = document.getElementById('happy');
  const party = document.getElementById('party');

  mood_slider.addEventListener("input", function() {
    const value = mood_slider.value;
    const moodValues = ['focus', 'study', 'neutral', 'happy', 'party'];
    const colorValues = []
    
    
  });

  const tempo_slider = document.getElementById("tempo-slider");
  const slowLabel = document.getElementById("slow");
  const mediumLabel = document.getElementById("medium");
  mediumLabel.style.textShadow = "0 0 5px orange, 0 0 10px orange, 0 0 15px orange, 0 0 20px orange, 0 0 35px orange, 0 0 40px orange, 0 0 50px orange, 0 0 75px orange";
  const fastLabel = document.getElementById("fast");
  
  tempo_slider.addEventListener("input", function() {
    const value = tempo_slider.value;
    console.log(value);
    if (value == 1) {
      console.log('Slow');
      slowLabel.style.textShadow = "0 0 5px blue, 0 0 10px blue, 0 0 15px blue, 0 0 20px blue, 0 0 35px blue, 0 0 40px blue, 0 0 50px blue, 0 0 75px blue";
      mediumLabel.style.textShadow = "";
      fastLabel.style.textShadow = "";
    } else if (value == 2) {
      console.log('Medium');
      slowLabel.style.textShadow = "";
      mediumLabel.style.textShadow = "0 0 5px orange, 0 0 10px orange, 0 0 15px orange, 0 0 20px orange, 0 0 35px orange, 0 0 40px orange, 0 0 50px orange, 0 0 75px orange";
      fastLabel.style.textShadow = "";
    } else {
      console.log('Fast');
      slowLabel.style.textShadow = "";
      mediumLabel.style.textShadow = "";
      fastLabel.style.textShadow = "0 0 5px red, 0 0 10px red, 0 0 15px red, 0 0 20px red, 0 0 35px red, 0 0 40px red, 0 0 50px red, 0 0 75px red";
    }
  });

    var select = function(s) {
      return document.querySelector(s);
    },
    selectAll = function(s) {
      return document.querySelectorAll(s);
    }, 
    animationWindow = select('#animationWindow'),    
      animData = {
      wrapper: animationWindow,
      animType: 'svg',
      loop: true,
      prerender: true,
      autoplay: true,
      path: 'https://s3-us-west-2.amazonaws.com/s.cdpn.io/35984/play_fill_loader.json',
    rendererSettings: {
      //context: canvasContext, // the canvas context
      //scaleMode: 'noScale',
      //clearCanvas: false,
      //progressiveLoad: false, // Boolean, only svg renderer, loads dom elements when needed. Might speed up initialization for large number of elements.
      //hideOnTransparent: true //Boolean, only svg renderer, hides elements when opacity reaches 0 (defaults to true)
    }   
    }, anim;

    anim = bodymovin.loadAnimation(animData);
  anim.addEventListener('DOMLoaded', onDOMLoaded);


  function onDOMLoaded(e){
  
  anim.addEventListener('complete', function(){});
  }

  // Start observing the element for changes
  observer.observe(elementToObserve, { childList: true });

    $("#song-name-button").click(function() {
      const songList = document.getElementById('searched-songs');
      var songName = $("#song-name-input").val();
      console.log(songName)

      $.ajax({
        type: "POST",
        url: "/search",
        data: {
          songName: songName
        },
        success: function(response) {
          
          songList.innerHTML = ""
          console.log('Search success! response:')
          console.log(response);

          const songInputField = document.getElementById('song-name-input');
          const selectedSongs = document.getElementById('selected-songs');

          
          response.forEach(song => {
            const li = document.createElement('li');

            li.innerHTML = `
              <div class="search-song-container" style="cursor:pointer">
                <div class="search-song-image-container">
                  <img src="${song.album_image_url}" alt="Song Image" class="song-image">
                </div>
                <div class="song-details">
                  <h2 class="song-name">${song.name}</h2>
                  <p class="song-year">${song.year}</p>
                </div>
              </div>
            `;
            
            songList.appendChild(li);

            li.addEventListener('click', function(e){
              console.log(song.name, ' added!')
              songList.innerHTML = ""
              songInputField.value = ""

              newSong = document.createElement('li')
              newSong.innerHTML = `
                <div class="selected-song-container" style="cursor:pointer">
                  <div class="search-song-image-container">
                    <img src="${song.album_image_url}" alt="Song Image" class="song-image">
                  </div>
                  <div class="song-details">
                    <h2 class="selected-song-name">${song.name}</h2>
                    <p class="song-year">${song.year}</p>
                  </div>
                </div>
              `
              selectedSongs.appendChild(newSong)
              
              $.ajax({
                type: "POST",
                url: "/get_audio_features",
                data: {
                  id: song.id
                },
                success: function(response) {
                  console.log('Audio feautres for song ID ', song.id, response);
                }
              });

            });
              
            });

          songList.addEventListener('click', function(e) {
            // Check if the clicked element is a list item
            if (e.target && e.target.nodeName === 'LI') {
              // Get the song name and year from the clicked list item
              const songName = e.target.querySelector('.song-name').textContent;
              const songYear = e.target.querySelector('.song-year').textContent;
        
              // Execute a function with the song name and year
              console.log(`Clicked song: ${songName} (${songYear})`);
            }
          });
        }
      });
    });
  
    $("#get-recommendations-button").click(function() {

      var advancedSearchOptions = document.getElementById("advancedSearchOptions");
      console.log(advancedSearchOptions.style.display);
      
      explicit = startYear = endYear = tempo = mood = "None"
      
      if (advancedSearchOptions.style.display === "block") {
        explicit = document.getElementById('explicit').checked;
        console.log(explicit);
        
        rangeValue = document.getElementById('range-values').innerHTML
        startYear = rangeValue.slice(0, 4);
        endYear = rangeValue.slice(-4)
        console.log('Year: ', startYear, endYear);

        tempo = document.getElementById('tempo-slider').value
        console.log(tempo);

        mood = document.getElementById('mood-slider').value
        console.log(mood);
        filters = { 'explicit': explicit, 'startYear': startYear, 'endYear': endYear,'tempo':  tempo, 'mood': mood}
        console.log(filters);
      }

      console.log('Explicit: ', explicit, ' Year ', startYear, endYear, ' Tempo: ', tempo, ' Mood: ', mood);

      recommendations_div = document.getElementById('get-recommendations-div');
      animationWindowElement = document.getElementById('animationWindow');
      left_half = document.getElementById('left-half')
      right_half = document.getElementById('right_half')
      recommendations_div.innerHTML = '';
      console.log(animationWindowElement.style.display)
      animationWindowElement.style.display = 'block';
      console.log(animationWindowElement.style.display)

      const colorElement = document.querySelector("#animationWindow > svg > g > g:nth-child(2) > g > path");
      const anotherColorElement = document.querySelector("#animationWindow > svg > g > g:nth-child(6) > g > path");

      colorElement.setAttribute('stroke', 'rgb(0,166,81)')
      anotherColorElement.setAttribute('fill', 'rgb(0,166,81)')

      $.ajax({
        type: "POST",
        url: "/get_recommendations",
        data: {
          explicit: explicit,
          startYear: startYear,
          endYear: endYear,
          tempo: tempo,
          mood: mood
        },
        success: function(response) {

          console.log(response);
          left_half.classList.add("addedclass");
          right_halfclassList.add("addedclass");
          animationWindowElement.style.display = 'none';
 
          recommendationsList = document.getElementById("song-recommendations-list");

          response.forEach(song => {
            const li = document.createElement('li');

            
            li.innerHTML = `
                <div class="rec-song-card" style="cursor:pointer; max-width: 500px">
                  <div class='rec-song-image-container'>
                    <img src="${song.image_url}" alt="Song Image" class="rec-song-image">
                    <div class="overlay">
                      <a href="#" class="icon" title="User Profile">
                      <img src="static/images/play-icon.png">
                      </a>
                    </div>
                  </div>
                  <div class="rec-song-details">
                    <h2 class="song-title">${song.name}</h2>
                    <p class="rec-song-release-year">${song.year}</p>
                    <p class="rec-song-album">${song.album}</p>
                    <p class="rec-song-artists">${song.artist}</p>
                  </div>
                </div>
            `;
            
            li.addEventListener('click', function(e) {
              window.location.href = song.url;
            })
            recommendationsList.appendChild(li);
            
            recommendations_div.innerHTML = "<h2>Recommended Songs for you</h2>"
          });
        }
      });
    });

    $("#advanced-search-button").click(function() {
      var advancedSearchOptions = document.getElementById("advancedSearchOptions");
      console.log(advancedSearchOptions.style.display);
      if (advancedSearchOptions.style.display === "none") {
        advancedSearchOptions.style.display = "block";
      } else {
        advancedSearchOptions.style.display = "none";
      }
    });
});
  



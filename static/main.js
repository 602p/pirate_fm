var thumbnailCache={};
var currentCache;
var currentSong;
var currentPlaylist;
var currentPlaylistPosition;
var lastApiCallResult;
var isPlayingPlaylist=false;

function GetQueryStringParams(sParam){
    var sPageURL = window.location.search.substring(1);
    var sURLVariables = sPageURL.split('&');
    for (var i = 0; i < sURLVariables.length; i++)
    {
        var sParameterName = sURLVariables[i].split('=');
        if (sParameterName[0] == sParam)
        {
            return sParameterName[1];
        }
    }
}

function playSong(songid){
	updateCachedata(1);
	currentSong=songid;
	$.ajax("http://192.168.1.60:5000/invoke/"+songid);
	
	setThumbnail(songid);
	
	if (currentCache.valid_caches.indexOf(songid)!=-1){
		return true;
	}
	return false;
}

function setThumbnail(songid){
	if (thumbnailCache[songid]==undefined)
		$.getJSON("https://www.googleapis.com/youtube/v3/videos?part=snippet&id="+songid+"&key="+apiKey).done(
			function(d){
				lastApiCallResult=d;
				for (var i = 0; i < d.items.length; i++) {
					thumbnailCache[songid]=
						d.items[i].snippet.thumbnails.high.url;
				}
				$("#nowplaying_thumb").attr("src",thumbnailCache[songid]);

			}
		);
	else
		$("#nowplaying_thumb").attr("src",thumbnailCache[songid]);
	$("#nowplaying_name").text(currentCache.name_mappings[songid]);
}

function playPlaylist(plid){
	currentPlaylist=[];
	currentPlaylistPosition=-1;
	isPlayingPlaylist=true;
	$.getJSON("https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=50&playlistId="+plid+"&key="+apiKey).done(
		function(d){
			lastApiCallResult=d;
			for (var i = 0; i < d.items.length; i++) {
				currentPlaylist.push(d.items[i].snippet.resourceId.videoId);
				thumbnailCache[d.items[i].snippet.resourceId.videoId]=
					d.items[i].snippet.thumbnails.high.url;
			}
			playNextPlaylistSong();
		}
	);
}

function playNextPlaylistSong(){
	currentPlaylistPosition+=1;
	if (currentPlaylistPosition==currentPlaylist.length){
		isPlayingPlaylist=false;
		return;
	}
	playSong(currentPlaylist[currentPlaylistPosition]);
}

function stopSong(){
	$.ajax("http://192.168.1.60:5000/stop");
	;
}

function updateCachedata(async){
	$.ajax({
	  url: "http://192.168.1.60:5000/get",
	  dataType: 'json',
	  async: async}).done(
		function(d){
			currentCache=d;
		}
	);
}

function checkPlayingState(){
	$.getJSON("http://192.168.1.60:5000/nowplaying").done(
		function(d){
			if (!d.playing){
				if (isPlayingPlaylist){
					playNextPlaylistSong();
				}
			}else{
				setThumbnail(d.url);
			}
			$("#playing_status").text(d.playing?"Playing":"Not Playing");
		}
	);
}

function checkQSCommands(){
	updateCachedata(0);
	if (GetQueryStringParams("playlist")!=undefined){
		playPlaylist(GetQueryStringParams("playlist"));
	}else if(GetQueryStringParams("song")!=undefined){
		playSong(GetQueryStringParams("song"));
	}
	setInterval(checkPlayingState, 500)
}
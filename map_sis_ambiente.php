<?php 
  $col = pg_escape_string($_GET['c']);
  $giro = pg_escape_string($_GET['g']);
  require('./conn.php');
?>

<!DOCTYPE html>
<html>
  <head>
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
    <meta charset="utf-8">
    <title>KML Click Capture Sample</title>
    <style>
      html, body {
        height: 100%;
        padding: 0;
        margin: 0;
        }
      #map {
       /*height: 360px;
       width: 300px;*/
       height: 100%;
       width: 100%;
       overflow: hidden;
       float: left;
       border: thin solid #333;
       }
      #capture {
       height: 360px;
       width: 480px;
       overflow: hidden;
       float: left;
       background-color: #ECECFB;
       border: thin solid #333;
       border-left: none;
       }
    </style>
  </head>
  <body>
    <div id="map"></div>
    <!--div id="capture"></div-->
    <script>
      var map;
      //var src = 'https://developers.google.com/maps/documentation/javascript/examples/kml/westcampus.kml';
      var src = 'https://gishosting.gter.it/sa/kml_sis_ambiente.php?c=<?php echo $col;?>&g=<?php echo $giro;?>';

      function initMap() {
        map = new google.maps.Map(document.getElementById('map'), {
          center: new google.maps.LatLng(-19.257753, 146.823688),
          zoom: 2,
          mapTypeId: 'terrain'
        });

        var kmlLayer = new google.maps.KmlLayer(src, {
          suppressInfoWindows: true,
          preserveViewport: false,
          map: map
        });
        /*kmlLayer.addListener('click', function(event) {
          var content = event.featureData.infoWindowHtml;
          var testimonial = document.getElementById('capture');
          testimonial.innerHTML = content;
        });*/
      }
    </script>
    <script async
    src="https://maps.googleapis.com/maps/api/js?key=<?php echo $G_API_KEY;?>&callback=initMap">
    </script>
  </body>
</html>

<?php
echo '';
?>
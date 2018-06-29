{% extends "header.html" %}

{% block scripts %}

<script> 
    function draw_side_pics(){
  var paper=$( ".paper" );
var article = $( ".col-sm-12" );
var article_num=article.length;
if (article_num>4){
    article_num=4
};
var paperwidth=paper.width();
var paperheight=paper.height();
var articlewidth=article.width();
var articleheight=article.height();
var lefty=$( ".col-sm-12:nth-child(1)").position().left;

var lefts_array=[$( ".col-sm-12:nth-child(1)").position().left];
for (i=2;i<article_num+1;i++){
    lefts_array.push($( ".col-sm-12:nth-child("+i+")").position().left)
};
var leftmost=Math.min(...lefts_array)+20;
var rightmost=Math.max(...lefts_array)+articlewidth;
var rightdist=paperwidth-rightmost+100;
    if(window.innerWidth<380){
        rightdist=0
    };
    if (rightdist>100){
        rightdist=100
    };
var leftdist=leftmost;
    if (leftdist>100){
        leftdist=100
    };
    var i;
    if (rightdist>50){
       for (i=0;i< paperheight/(rightdist+5);i++) {
          $(".arts").append("<div class='test' "
    +  " style='position: absolute;bottom:"+
        (i*(rightdist+5)+5)+"px; left:"+(rightmost+5)+
            "px;height:"+rightdist+"px;width:"+rightdist+
        "px;'><img src='{{url_for('static',filename="")}}"+get_random_file_name()+"' style='width:100%;height:100%;'> </div>"); 
       }};
    if (leftdist>50){
    for (i=0;i< paperheight/(leftdist+5);i++) {
          $(".arts").append("<div class='test' "
    +  " style='position: absolute;bottom:"+
        (i*(leftdist+5)+5)+"px; left:"+(leftmost-leftdist-5)+
            "px;height:"+leftdist+"px;width:"+leftdist+
        "px;'><img src='{{url_for('static',filename="")}}"+get_random_file_name()+"' style='width:100%;height:100%;'> </div>"); 
       }; } 
};
   $(document).ready(function(){
       random_title();
       draw_side_pics();
     
    $( "#cater" ).click(function(){
      $('.submen').toggle();  
    });  
   
$(window).resize(function() {
     $(".test").remove();
    clearTimeout(window.resizedFinished);
    window.resizedFinished = setTimeout(function(){
        draw_side_pics();
        hide_title()
    }, 1000);
});       

     
       
   })   
      </script>
{% endblock %}

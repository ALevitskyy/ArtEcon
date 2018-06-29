function get_random_file_name(){
var rand_num=Math.floor(Math.random() * 801)+100; 
var file_string="image"
if (rand_num<10){
   file_string=file_string+"0"+"0"+rand_num+".png" 
} else if (rand_num<100){
    file_string=file_string+"0"+rand_num+".png" 
} else{
  file_string=file_string+rand_num+".png"  
}
return "play/"+file_string
};
function random_title(){
  myArray=["<span class='vitty_title' style='color:orange;overflow:hidden;'>Technology</span>+<span class='vitty_title' style='color:red;overflow:hidden;'>Economics</span>=<span class='vitty_title' style='color:#CCCC00;overflow:hidden;'>Art</span>","<span class='vitty_title' style='color:orange;overflow:hidden;'>Artificial Economist - Your Guide to the World of Economics</span>","<span class='vitty_title'  style='color:green;overflow:hidden;'>Understanding The Coordinate System of the New World</span>"];
   var rand = myArray[Math.floor(Math.random() * myArray.length)];
       $(".headdiv").append(rand); 
} ;
function hide_title(){
    if(window.innerWidth<492){
        $(".headdiv").css("visibility","hidden")
    } else {
        $(".headdiv").css("visibility","visible")
        
    }
};
function sort_button(){
$( "#orange_button" ).click(function(){
      $('.submen').hide(); 
        $( "#orange_button" ).css("background-color","#CCCC00");
    }); }
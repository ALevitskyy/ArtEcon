function append_table(){
        $('.table_div').append('<div id="table_div"><table id="actions" class="display" width="80%"> <thead> <tr><th>ID</th><th>Currency</th><th>Size</th><th>Order</th><th>Initial Price</th><th>Current/Close Price</th><th>Start Date</th><th>Current/Close Date</th><th>Status</th><th>Profit</th></tr></thead></table></div>');
    }
    function update_cashes(data){
        $("#free_cash").text(data.free_cash.toString());
        $("#total_cash").text(data.total_cash.toString());
    }
    function process_log(data){
       if($("#actions").length != 0) {
                      $("#table_div").remove();
                        append_table();
                        
};
   //Load  datatable
    var oTblReport = $("#actions");
 try{
    oTblReport.DataTable ({
        "data" : data.log,
        "columns" : [
            { "data" : "id" },
            { "data" : "currency" },
            { "data" : "size" },
            { "data" : "order" },
            { "data" : "initial_price" },
            { "data" : "current_price" },
            { "data" : "start_date" },
            { "data" : "close_date" },
            { "data" : "status" },
            { "data" : "profit" }
        ]
    });
     } catch(e){
              $(".sorting").first().click();} 
    }
    function close_tab (tab_li)
{
    var tabContentId = $(tab_li).parent().attr("href");
    
     //remove li of tab
    if ($(tabContentId).is(":visible")) {
        var was_active=true;    
    };
    /*var index_to_delete=$(".nav-tabs li").index($(tab_li).parent().parent());
    console.log(index_to_delete);
    displayed_graphs.splice(index_to_delete,1);*/
    $(tab_li).parent().parent().remove();
    if (was_active){
        var li_list = $(tab_li).parent().parent().parent();
        li_list.find("a").eq(0).tab('show'); // Select first tab
    };
    
    $(tabContentId).remove(); //remove respective tab content
};
function makeid() {
  var text = "";
  var possible = "abcdefghijklmnopqrstuvwxyz";

  for (var i = 0; i < 7; i++)
    text += possible.charAt(Math.floor(Math.random() * possible.length));

  return text;
};
   
function main_form_submit(e){
 var rand_id=makeid();
var link_text= $('.currency-form').find(":selected").text()+'   '+$('.type-form').find(":selected").text()
    $(".nav-tabs").append('<li><a data-toggle="tab" href="#'+
                    rand_id+'">'+
            link_text+'<button class="close closeTab" type="button" onclick="close_tab(this)" >×</button>' +'</a></li>');
    
            $(".tab-content").append('<div id="'+rand_id+
                                     '" class="tab-pane fade in active"></div>');
            
            
            var url = "{{ url_for('.getData') }}"; // send the form data here.
            var margin = {top: 20, right: 50, bottom: 30, left: 50},
            width = $( window ).width() - margin.left - margin.right-70,
            height = $( window ).height()*4/5 - margin.top - margin.bottom-15;

    var parseDate = d3.timeParse("%Y-%m-%d %H:%M:%S");

    var x = techan.scale.financetime()
            .range([0, width]);

    var y = d3.scaleLinear()
            .range([height, 0]);
        
    var zoom = d3.zoom()
            .on("zoom", zoomed);

    var zoomableInit;
    var candlestick = techan.plot.candlestick()
            .xScale(x)
            .yScale(y);
    function zoomed() {
        var rescaledY = d3.event.transform.rescaleY(y);
        yAxis.scale(rescaledY);
        candlestick.yScale(rescaledY);

        // Emulates D3 behaviour, required for financetime due to secondary zoomable scale
        x.zoomable().domain(d3.event.transform.rescaleX(zoomableInit).domain());

        draw();
    };

    function draw() {
        svg.select("g.candlestick").call(candlestick);
        // using refresh method is more efficient as it does not perform any data joins
        // Use this if underlying data is not changing
//        svg.select("g.candlestick").call(candlestick.refresh);
        svg.select("g.x.axis").call(xAxis);
        svg.select("g.y.axis").call(yAxis)
    };
    var xAxis = d3.axisBottom(x);

    var xTopAxis = d3.axisTop(x);

    var yAxis = d3.axisLeft(y);

    var yRightAxis = d3.axisRight(y);

    var ohlcAnnotation = techan.plot.axisannotation()
            .axis(yAxis)
            .orient('left')
            .format(d3.format(',.2f'));

    var ohlcRightAnnotation = techan.plot.axisannotation()
            .axis(yRightAxis)
            .orient('right')
            .translate([width, 0]);

    var timeAnnotation = techan.plot.axisannotation()
            .axis(xAxis)
            .orient('bottom')
            .format(d3.timeFormat("%Y-%m-%d %H:%M:%S"))
            .width(65)
            .translate([0, height]);

    var timeTopAnnotation = techan.plot.axisannotation()
            .axis(xTopAxis)
            .orient('top');

    var crosshair = techan.plot.crosshair()
            .xScale(x)
            .yScale(y)
            .xAnnotation([timeAnnotation, timeTopAnnotation])
            .yAnnotation([ohlcAnnotation, ohlcRightAnnotation])
            .on("enter", enter)
            .on("out", out)
            .on("move", move);

    var svg = d3.select('#'+rand_id).append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var coordsText = svg.append('text')
            .style("text-anchor", "end")
            .attr("class", "coords")
            .attr("x", width - 5)
            .attr("y", 15);
            $.ajax({
                type: "POST",
                url: url,
                data: $('.main_form').serialize(), // serializes the form's elements.
                success: function (data) {
                    if(data.errorrs=== undefined)  {
                    console.log(data);
               //     displayed_graphs.push($(".main_form").serializeArray());
                    var accessor = candlestick.accessor();
        data = data.map(function(d) {
            return {
                date: parseDate(d.date),
                open: +d.open,
                high: +d.high,
                low: +d.low,
                close: +d.close,
                volume: +0
            };
        }).sort(function(a, b) { return d3.ascending(accessor.d(a), accessor.d(b)); });
        x.domain(data.map(accessor.d));
        y.domain(techan.scale.plot.ohlc(data, accessor).domain());
        zoomableInit = x.zoomable().clamp(false).copy();        
        svg.append("clipPath")
            .attr("id", "clip")
        .append("rect")
            .attr("x", 0)
            .attr("y", y(1))
            .attr("width", width)
            .attr("height", y(0) - y(1));
        svg.append("g")
                .datum(data)
                .attr("class", "candlestick")
                .call(candlestick);

        svg.append("g")
               .attr("class", "x axis")
                .call(xTopAxis);

        svg.append("g")
                .attr("class", "x axis")
                .attr("transform", "translate(0," + height + ")")
                .call(xAxis);

        svg.append("g")
                .attr("class", "y axis")
                .call(yAxis);

        svg.append("g")
                .attr("class", "y axis")
                .attr("transform", "translate(" + width + ",0)")
                .call(yRightAxis);

        svg.append("g")
                .attr("class", "y annotation left")
                .datum([{value: 74}, {value: 67.5}, {value: 58}, {value:40}]) // 74 should not be rendered
                .call(ohlcAnnotation);

        svg.append("g")
                .attr("class", "x annotation bottom")
                .datum([{value: x.domain()[30]}])
                .call(timeAnnotation);

        svg.append("g")
                .attr("class", "y annotation right")
                .datum([{value: 61}, {value:52}])
                .call(ohlcRightAnnotation);

        svg.append("g")
                .attr("class", "x annotation top")
                .datum([{value: x.domain()[80]}])
                .call(timeTopAnnotation);
        svg.append("rect")
            .attr("class", "pane")
            .attr("width", width)
            .attr("height", height)
            .call(zoom);
                    
        svg.append('g')
                .attr("class", "crosshair")
                .datum({ x: x.domain()[80], y: 67.5 })
                .call(zoom)
                .call(crosshair)
                .each(function(d) { move(d); }); // Display the current data
                
        
        svg.append('text')
                .attr("x", 5)
                .attr("y", 15)
                .text(link_text);
        
    
                    
                    
                    
                    
                    
                    
                    // display the returned data in the console.
                }else{ 
    
    alert("You have an error! Check the error log!");
    $('#error-log').append('<p>'+JSON.stringify(data.errorrs)+'</p>'); }}
            });
            $('.nav-tabs li:eq('+($(".nav-tabs li").length-1).toString()+') a').tab('show');
            e.preventDefault(); // block the traditional submission of the form.
        
        function enter() {
        coordsText.style("display", "inline");
    }

    function out() {
        coordsText.style("display", "none");
    }

    function move(coords) {
        coordsText.text(
            timeAnnotation.format()(coords.x) + ", " + ohlcAnnotation.format()(coords.y)
        );
    };                           
};

function load_all(){
    $(".currency-form option").each(function()
{
    $(".currency-form").val($(this).val());
    $(".main_form").submit();
});
}
function close_all(){
    $(".nav-tabs li").each(function(){
    close_tab($(this).find("button"));
                           })
}
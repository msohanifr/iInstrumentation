
//this has to be changed to id
var sts = document.getElementsByClassName('sts');
var items = document.getElementsByClassName('progress');
for (var i=0;i<items.length; i++){
    var mychildren = items[i].children;
    var mystat = sts[i].innerHTML;
    for (j=0; j< mychildren.length; j++){

        if (mychildren[j].getAttribute('data-step')==1 & mystat=='Order Received'){
            mychildren[j].className="is-active";
        }
        if (mychildren[j].getAttribute('data-step')==2 & mystat=='Pickup Scheduled'){
            mychildren[j].className="is-active";
        }
        if (mychildren[j].getAttribute('data-step')==3 & mystat=='Picked Up and In Process'){
            mychildren[j].className="is-active";
        }
        if (mychildren[j].getAttribute('data-step')==4 & mystat=='Delivery Scheduled'){
            mychildren[j].className="is-active";
        }
        if (mychildren[j].getAttribute('data-step')==5 & mystat=='Delivered'){
            mychildren[j].className="is-active";
        }
    }

}
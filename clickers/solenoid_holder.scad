
w = 16;
h = 16;
wall = 3;
strike = 7;

union() {
    difference() {
        linear_extrude(40) {
            polygon(points=[[0,0],[0,wall+h],[wall,wall+h],[wall,wall],[wall*2+w,wall],[wall*2+w,0]]);
        };
        translate([11,-1,2+7+strike]) {
            rotate([0,90,90]) {
                cylinder(5,1.5,1.5, $fn=100);
            }
        }
        translate([11,-1,2+7+15+strike]) {
            rotate([0,90,90]) {
                cylinder(5,1.5,1.5, $fn=100);
            }
        }

    }
    polygon(points=[[0,0],[0,wall+h],[wall,wall+h],[wall,wall],[wall+w,wall],[wall+w,0]]);
    translate([0,0,-1]) {
    cube([wall*2+w,wall+h,wall]);
    }

    translate([wall*2+w,wall,wall-1]) {
        rotate([0,270,0]) {
            linear_extrude(wall) {
                polygon(points=[
                    [0,0],
                    [wall+h,0],
                    [0,w]
                    ]);
            }
        }
    }
    
}
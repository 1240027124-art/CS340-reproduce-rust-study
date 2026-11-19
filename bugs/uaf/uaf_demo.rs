use std::ptr;

fn main() {
    let mut x = Box::new(100);
    let p = &mut *x as *mut i32;
    drop(x);

    unsafe {
        *p = 200;
        println!("value: {}", *p);
    }
}

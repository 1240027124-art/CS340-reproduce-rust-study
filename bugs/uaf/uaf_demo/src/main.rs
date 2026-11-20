fn main() {
    let a = Box::new(100);
    let p = Box::into_raw(a);
    unsafe {
        let _ = Box::from_raw(p);
        *p = 200;
        println!("{}", *p);
    }
}
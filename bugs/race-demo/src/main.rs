use std::thread;
use std::sync::Arc;
use std::sync::atomic::AtomicUsize;

fn main() {
    let data = Arc::new(AtomicUsize::new(0));
    let mut handles = vec![];

    for _ in 0..2 {
        let data_clone = Arc::clone(&data);
        let handle = thread::spawn(move || {
            unsafe {
                let ptr = &data_clone as *const Arc<AtomicUsize> as *mut Arc<AtomicUsize>;
                
                let inner_ptr = (*ptr).as_ptr();
                
                let current = *inner_ptr;
                for _ in 0..1000 { std::hint::black_box(0); }
                *inner_ptr = current + 1;
            }
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }
}

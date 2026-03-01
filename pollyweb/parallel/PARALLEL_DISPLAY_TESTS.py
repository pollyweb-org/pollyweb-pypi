class PARALLEL_DISPLAY_TESTS:



    @classmethod
    def TestParallelDisplay(cls):

        from .PARALLEL_DISPLAY import PARALLEL_DISPLAY
        from .PARALLEL_DISPLAY_SLOT import PARALLEL_DISPLAY_SLOT

        import time
        threads = 4
        display = PARALLEL_DISPLAY(threads= threads)
        
        slots:list[PARALLEL_DISPLAY_SLOT] = []
        for i in range(threads):
            slot = display.StartSlot(f'Test {i+1}')
            slots.append(slot)

        for i in range(3):
            for iSlot in range(threads):
                time.sleep(0.05)
                slot = slots[iSlot]
                slot.Finish(f'Loop {i+1} on slot={slot.GetID()}')

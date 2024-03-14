# container.py

class Container:
    '''Class for storing container attributes'''

    def __init__(self, id, name, cpu, memory):
        self.name = str(name)
        self.id = str(id)
        self.cpu = float(cpu)
        self.memory = float(memory)

    @property
    def id(self):
        '''Return container ID'''
        return self._id

    @id.setter
    def id(self, id):
        '''Set container ID'''
        self._id = id

    @property
    def name(self):
        '''Return container name'''
        return self._name

    @name.setter
    def name(self, name):
        '''Set container name'''
        self._name = name

    @property
    def cpu(self):
        '''Return container cpu usage'''
        return self._cpu

    @cpu.setter
    def cpu(self, cpu):
        '''Set container cpu usage'''
        self._cpu = cpu

    @property
    def memory(self):
        '''Return container memory usage'''
        return self._memory

    @memory.setter
    def memory(self, memory):
        '''Set container memory usage'''
        self._memory = memory

    def __str__(self):
        '''String representation of container'''
        return f'{self.name:<20s} {self.cpu:<5} {self.memory:<5}'